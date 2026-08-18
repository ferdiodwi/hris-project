from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from payroll.models import (
    PayrollProfile,
    PayrollRun,
    Payslip,
    SalaryComponent,
)

from .bpjs_service import calculate_bpjs

from .pph21_service import (
    calculate_monthly_pph21,
    calculate_final_period_pph21,
)


D = Decimal


def decimal_value(value):
    return D(str(value or 0))


def serialize_decimals(data):
    result = {}

    for key, value in data.items():
        if isinstance(value, Decimal):
            result[key] = str(value)
        else:
            result[key] = value

    return result


def calculate_employee_payroll(
    payroll_run,
    profile,
    components,
    previous_payslips,
):
    earnings = D("0")
    other_deductions = D("0")

    # =====================================
    # Salary Component PAY-01
    # =====================================

    for component in components:
        component_type = (
            component.component_type
            or ""
        ).lower()

        if component_type == "earning":
            earnings += decimal_value(
                component.amount
            )

        elif component_type == "deduction":
            other_deductions += decimal_value(
                component.amount
            )

    gross_salary = earnings

    # =====================================
    # BPJS
    # =====================================

    bpjs = calculate_bpjs(
        wage=profile.bpjs_wage,
        jkk_risk=profile.jkk_risk,

        ketenagakerjaan_active=(
            profile.bpjs_ketenagakerjaan_active
        ),

        kesehatan_active=(
            profile.bpjs_kesehatan_active
        ),
    )

    # Gross untuk PPh21 bukan hanya gross_salary.
    # JKK + JKM + BPJS Kesehatan perusahaan
    # termasuk penghasilan bruto pajak.

    tax_gross = (
        gross_salary
        + bpjs[
            "taxable_employer_contribution"
        ]
    )

    # =====================================
    # PPH 21
    # =====================================

    if payroll_run.period_month != 12:

        tax = calculate_monthly_pph21(
            gross_income=tax_gross,
            ptkp_status=profile.ptkp_status,
        )

    else:

        previous_tax_gross = D("0")
        previous_retirement = D("0")
        previous_pph21 = D("0")

        for payslip in previous_payslips:

            detail = (
                payslip.calculation_detail
                or {}
            )

            previous_tax_gross += decimal_value(
                detail.get(
                    "tax_gross",
                    0,
                )
            )

            previous_retirement += decimal_value(
                detail.get(
                    "employee_retirement_contribution",
                    0,
                )
            )

            previous_pph21 += decimal_value(
                payslip.pph21_amount
            )

        annual_tax_gross = (
            previous_tax_gross
            + tax_gross
        )

        annual_retirement = (
            previous_retirement
            + bpjs[
                "employee_retirement_contribution"
            ]
        )

        months_worked = (
            len(previous_payslips)
            + 1
        )

        tax = calculate_final_period_pph21(
            annual_gross_income=annual_tax_gross,

            employee_retirement_contribution=(
                annual_retirement
            ),

            ptkp_status=profile.ptkp_status,

            previous_pph21=previous_pph21,

            months_worked=months_worked,
        )

    pph21_amount = decimal_value(
        tax["amount"]
    )

    bpjs_amount = decimal_value(
        bpjs["employee_total"]
    )

    # =====================================
    # TOTAL DEDUCTION
    # =====================================

    total_deduction = (
        other_deductions
        + bpjs_amount
        + pph21_amount
    )

    # =====================================
    # NET SALARY
    # =====================================

    net_salary = (
        gross_salary
        - total_deduction
    )

    calculation_detail = {
        "tax_gross": str(
            tax_gross
        ),

        "ptkp_status":
            profile.ptkp_status,

        "bpjs_wage": str(
            profile.bpjs_wage
        ),

        "employee_retirement_contribution": str(
            bpjs[
                "employee_retirement_contribution"
            ]
        ),

        "other_deductions": str(
            other_deductions
        ),

        "bpjs": serialize_decimals(
            bpjs
        ),

        "pph21": serialize_decimals(
            tax
        ),
    }

    return {
        "gross_salary":
            gross_salary,

        "pph21_amount":
            pph21_amount,

        "bpjs_amount":
            bpjs_amount,

        "total_deduction":
            total_deduction,

        "net_salary":
            net_salary,

        "calculation_detail":
            calculation_detail,
    }


def process_payroll_run(payroll_run):

    payroll_run.status = "processing"

    payroll_run.save(
        update_fields=[
            "status"
        ]
    )

    try:

        # =====================================
        # Ambil semua PayrollProfile sekaligus
        # =====================================

        profiles = list(
            PayrollProfile.objects
            .select_related("employee")
            .all()
        )

        if not profiles:
            raise ValueError(
                "Belum ada PayrollProfile."
            )

        employee_ids = [
            profile.employee_id
            for profile in profiles
        ]

        # =====================================
        # SalaryComponent hanya 1 query
        # =====================================

        components = list(
            SalaryComponent.objects.filter(
                employee_id__in=employee_ids,
                is_active=True,
            )
        )

        components_by_employee = defaultdict(
            list
        )

        for component in components:
            components_by_employee[
                component.employee_id
            ].append(
                component
            )

        # =====================================
        # Payslip periode sebelumnya
        # =====================================

        previous_payslips = list(
            Payslip.objects.filter(
                employee_id__in=employee_ids,

                payroll_run__period_year=(
                    payroll_run.period_year
                ),

                payroll_run__period_month__lt=(
                    payroll_run.period_month
                ),
            )
        )

        previous_by_employee = defaultdict(
            list
        )

        for payslip in previous_payslips:

            previous_by_employee[
                payslip.employee_id
            ].append(
                payslip
            )

        # =====================================
        # Kalkulasi di memory
        # =====================================

        payslips_to_create = []

        for profile in profiles:

            employee_id = (
                profile.employee_id
            )

            result = calculate_employee_payroll(
                payroll_run=payroll_run,

                profile=profile,

                components=(
                    components_by_employee[
                        employee_id
                    ]
                ),

                previous_payslips=(
                    previous_by_employee[
                        employee_id
                    ]
                ),
            )

            payslips_to_create.append(

                Payslip(
                    payroll_run=payroll_run,

                    employee_id=employee_id,

                    gross_salary=result[
                        "gross_salary"
                    ],

                    pph21_amount=result[
                        "pph21_amount"
                    ],

                    bpjs_amount=result[
                        "bpjs_amount"
                    ],

                    total_deduction=result[
                        "total_deduction"
                    ],

                    net_salary=result[
                        "net_salary"
                    ],

                    calculation_detail=result[
                        "calculation_detail"
                    ],
                )
            )

        # =====================================
        # Insert massal
        # =====================================

        with transaction.atomic():

            # Bisa process ulang payroll run
            Payslip.objects.filter(
                payroll_run=payroll_run
            ).delete()

            Payslip.objects.bulk_create(
                payslips_to_create,
                batch_size=500,
            )

            payroll_run.status = "completed"

            payroll_run.processed_at = (
                timezone.now()
            )

            payroll_run.save(
                update_fields=[
                    "status",
                    "processed_at",
                ]
            )

        return len(
            payslips_to_create
        )

    except Exception:

        payroll_run.status = "draft"

        payroll_run.save(
            update_fields=[
                "status"
            ]
        )

        raise
import csv

from io import StringIO

from payroll.models import Payslip


def generate_bank_csv(payroll_run):

    payslips = (
        Payslip.objects
        .filter(
            payroll_run=payroll_run
        )
        .select_related(
            "employee",
            "employee__payroll_profile",
        )
        .order_by("employee_id")
    )

    output = StringIO(
        newline=""
    )

    writer = csv.writer(
        output
    )

    writer.writerow([
        "reference_no",
        "employee_code",
        "employee_name",
        "bank_code",
        "account_number",
        "amount",
    ])

    missing_accounts = []

    for payslip in payslips:

        employee = (
            payslip.employee
        )

        profile = (
            employee.payroll_profile
        )

        if not payslip.bank_account_no:

            missing_accounts.append(
                employee.employee_code
            )

            continue

        writer.writerow([
            (
                f"PAY-{payroll_run.id}-"
                f"{payslip.id}"
            ),

            employee.employee_code,

            employee.full_name,

            profile.bank_code,

            payslip.bank_account_no,

            f"{payslip.net_salary:.2f}",
        ])

    if missing_accounts:
        raise ValueError(
            "Rekening belum tersedia untuk: "
            + ", ".join(
                missing_accounts[:10]
            )
        )

    return output.getvalue()
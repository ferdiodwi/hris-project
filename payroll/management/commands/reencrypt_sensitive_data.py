from django.core.management.base import (
    BaseCommand,
)

from accounts.models import Employee

from payroll.models import (
    PayrollProfile,
    Payslip,
    SalaryComponent,
)


class Command(BaseCommand):
    help = (
        "Re-encrypt semua data sensitif lama "
        "setelah migration PAY-03."
    )

    def handle(self, *args, **options):

        employee_count = 0
        component_count = 0
        profile_count = 0
        payslip_count = 0

        # =========================
        # NPWP
        # =========================

        for employee in Employee.objects.all():

            if employee.npwp_no:
                employee.save(
                    update_fields=[
                        "npwp_no"
                    ]
                )

                employee_count += 1

        # =========================
        # SALARY COMPONENT
        # =========================

        for component in (
            SalaryComponent.objects.all()
        ):

            fields = ["amount"]

            if component.rate_per_day is not None:
                fields.append(
                    "rate_per_day"
                )

            component.save(
                update_fields=fields
            )

            component_count += 1

        # =========================
        # PAYROLL PROFILE
        # =========================

        for profile in (
            PayrollProfile.objects.all()
        ):

            fields = [
                "bpjs_wage"
            ]

            if profile.bank_account_no:
                fields.append(
                    "bank_account_no"
                )

            profile.save(
                update_fields=fields
            )

            profile_count += 1

        # =========================
        # PAYSLIP
        # =========================

        for payslip in Payslip.objects.all():

            fields = [
                "gross_salary",
                "pph21_amount",
                "bpjs_amount",
                "total_deduction",
                "net_salary",
            ]

            if payslip.bank_account_no:
                fields.append(
                    "bank_account_no"
                )

            if payslip.pdf_password:
                fields.append(
                    "pdf_password"
                )

            payslip.save(
                update_fields=fields
            )

            payslip_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Re-encryption selesai."
            )
        )

        self.stdout.write(
            f"Employee NPWP : "
            f"{employee_count}"
        )

        self.stdout.write(
            f"SalaryComponent : "
            f"{component_count}"
        )

        self.stdout.write(
            f"PayrollProfile : "
            f"{profile_count}"
        )

        self.stdout.write(
            f"Payslip : "
            f"{payslip_count}"
        )
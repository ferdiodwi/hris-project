from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from payroll.models import (
    PayrollRun,
    Payslip,
)


class Command(BaseCommand):
    help = (
        "Sinkronkan nomor rekening PayrollProfile "
        "ke Payslip yang sudah dibuat."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--run-id",
            type=int,
            required=True,
        )

    def handle(self, *args, **options):
        run_id = options["run_id"]

        try:
            payroll_run = PayrollRun.objects.get(
                id=run_id
            )

        except PayrollRun.DoesNotExist:
            raise CommandError(
                f"PayrollRun ID {run_id} tidak ditemukan."
            )

        payslips = (
            Payslip.objects
            .filter(
                payroll_run=payroll_run
            )
            .select_related(
                "employee",
                "employee__payroll_profile",
            )
        )

        updated = 0
        missing = []

        for payslip in payslips:
            try:
                profile = (
                    payslip.employee.payroll_profile
                )

            except Exception:
                missing.append(
                    payslip.employee.employee_code
                )
                continue

            if not profile.bank_account_no:
                missing.append(
                    payslip.employee.employee_code
                )
                continue

            payslip.bank_account_no = (
                profile.bank_account_no
            )

            payslip.save(
                update_fields=[
                    "bank_account_no"
                ]
            )

            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Payslip rekening diperbarui: {updated}"
            )
        )

        if missing:
            self.stdout.write(
                self.style.WARNING(
                    "Masih belum punya rekening: "
                    + ", ".join(missing[:10])
                )
            )
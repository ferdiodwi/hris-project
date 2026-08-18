from django.core.management.base import BaseCommand

from payroll.models import PayrollProfile


class Command(BaseCommand):
    help = "Isi rekening dummy untuk testing PAY-03"

    def handle(self, *args, **options):
        profiles = PayrollProfile.objects.select_related(
            "employee"
        ).all()

        updated = 0

        for profile in profiles:
            if not profile.bank_account_no:
                profile.bank_code = "TESTBANK"

                profile.bank_account_no = (
                    f"999{profile.employee_id:09d}"
                )

                profile.save(
                    update_fields=[
                        "bank_code",
                        "bank_account_no",
                    ]
                )

                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Rekening dummy berhasil diisi: {updated}"
            )
        )
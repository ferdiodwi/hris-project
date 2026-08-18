from time import perf_counter

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from payroll.models import (
    PayrollProfile,
    PayrollRun,
    Payslip,
)

from payroll.services.payroll_service import (
    process_payroll_run,
)


class Command(BaseCommand):
    help = "Benchmark performa proses payroll PAY-02"

    def add_arguments(self, parser):
        parser.add_argument(
            "--run-id",
            type=int,
            required=True,
            help="ID PayrollRun yang akan diproses",
        )

        parser.add_argument(
            "--expected",
            type=int,
            default=1000,
            help="Jumlah minimal employee untuk benchmark",
        )

    def handle(self, *args, **options):
        run_id = options["run_id"]
        expected = options["expected"]

        # ================================
        # CEK JUMLAH DATA
        # ================================

        profile_count = (
            PayrollProfile.objects.count()
        )

        self.stdout.write("")
        self.stdout.write(
            "======================================"
        )
        self.stdout.write(
            "PAY-02 PAYROLL PERFORMANCE TEST"
        )
        self.stdout.write(
            "======================================"
        )

        self.stdout.write(
            f"PayrollProfile tersedia : {profile_count}"
        )

        self.stdout.write(
            f"Target benchmark        : {expected}"
        )

        if profile_count < expected:
            raise CommandError(
                f"Data tidak cukup. "
                f"Butuh minimal {expected} PayrollProfile, "
                f"tetapi hanya tersedia {profile_count}."
            )

        # ================================
        # CARI PAYROLL RUN
        # ================================

        try:
            payroll_run = PayrollRun.objects.get(
                id=run_id
            )

        except PayrollRun.DoesNotExist:
            raise CommandError(
                f"PayrollRun dengan ID {run_id} "
                f"tidak ditemukan."
            )

        self.stdout.write("")
        self.stdout.write(
            f"Payroll Run : {payroll_run.id}"
        )

        self.stdout.write(
            f"Periode     : "
            f"{payroll_run.period_month}/"
            f"{payroll_run.period_year}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Memulai proses payroll..."
        )

        # ================================
        # MULAI TIMER
        # ================================

        start_time = perf_counter()

        try:
            total_processed = process_payroll_run(
                payroll_run
            )

        except Exception as error:
            raise CommandError(
                f"Payroll gagal diproses: {error}"
            )

        # ================================
        # SELESAI TIMER
        # ================================

        end_time = perf_counter()

        elapsed_seconds = (
            end_time - start_time
        )

        elapsed_minutes = (
            elapsed_seconds / 60
        )

        # ================================
        # CEK PAYSLIP
        # ================================

        payslip_count = (
            Payslip.objects.filter(
                payroll_run=payroll_run
            ).count()
        )

        # ================================
        # HASIL
        # ================================

        self.stdout.write("")
        self.stdout.write(
            "======================================"
        )
        self.stdout.write(
            "HASIL BENCHMARK"
        )
        self.stdout.write(
            "======================================"
        )

        self.stdout.write(
            f"Employee diproses : {total_processed}"
        )

        self.stdout.write(
            f"Payslip dibuat     : {payslip_count}"
        )

        self.stdout.write(
            f"Waktu proses       : "
            f"{elapsed_seconds:.3f} detik"
        )

        self.stdout.write(
            f"Waktu proses       : "
            f"{elapsed_minutes:.3f} menit"
        )

        self.stdout.write(
            "Batas NFR          : 600 detik / 10 menit"
        )

        self.stdout.write("")

        # ================================
        # VALIDASI NFR
        # ================================

        if (
            elapsed_seconds <= 600
            and total_processed >= expected
            and payslip_count >= expected
        ):
            self.stdout.write(
                self.style.SUCCESS(
                    "RESULT: PASS"
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "NFR PAY-02 TERPENUHI."
                )
            )

        else:
            self.stdout.write(
                self.style.ERROR(
                    "RESULT: FAIL"
                )
            )

            self.stdout.write(
                self.style.ERROR(
                    "NFR PAY-02 BELUM TERPENUHI."
                )
            )
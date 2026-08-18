from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from accounts.models import Employee

from payroll.models import (
    PayrollProfile,
    SalaryComponent,
)


User = get_user_model()


class Command(BaseCommand):
    help = (
        "Membuat data test hingga 1000 employee "
        "untuk benchmark PAY-02."
    )

    TARGET_EMPLOYEES = 1000

    def handle(self, *args, **options):

        self.stdout.write("")
        self.stdout.write(
            "======================================"
        )
        self.stdout.write(
            "SEED PAYROLL PERFORMANCE DATA"
        )
        self.stdout.write(
            "======================================"
        )

        # ======================================
        # CEK EMPLOYEE YANG SUDAH ADA
        # ======================================

        existing_employee_count = (
            Employee.objects.count()
        )

        self.stdout.write(
            f"Employee saat ini : "
            f"{existing_employee_count}"
        )

        # ======================================
        # AMBIL JOB TITLE DARI DATA EXISTING
        # ======================================

        existing_employee = (
            Employee.objects
            .select_related("job_title")
            .first()
        )

        if existing_employee is None:
            raise CommandError(
                "Belum ada Employee sama sekali. "
                "Buat minimal 1 Employee terlebih dahulu."
            )

        if existing_employee.job_title_id is None:
            raise CommandError(
                "Employee pertama tidak memiliki JobTitle."
            )

        job_title = (
            existing_employee.job_title
        )

        self.stdout.write(
            f"JobTitle test     : {job_title}"
        )

        # ======================================
        # HITUNG JUMLAH YANG PERLU DIBUAT
        # ======================================

        employee_needed = max(
            0,
            self.TARGET_EMPLOYEES
            - existing_employee_count
        )

        self.stdout.write(
            f"Employee baru     : "
            f"{employee_needed}"
        )

        # ======================================
        # CREATE EMPLOYEE BARU
        # ======================================

        if employee_needed > 0:

            self.stdout.write("")
            self.stdout.write(
                "Membuat employee benchmark..."
            )

            start_number = (
                existing_employee_count + 1
            )

            end_number = (
                self.TARGET_EMPLOYEES + 1
            )

            created_count = 0

            for number in range(
                start_number,
                end_number,
            ):

                username = (
                    f"benchmark_user_{number:04d}"
                )

                email = (
                    f"benchmark{number:04d}"
                    f"@example.test"
                )

                employee_code = (
                    f"BENCH-{number:04d}"
                )

                # ==============================
                # USER
                # ==============================

                user, user_created = (
                    User.objects.get_or_create(
                        username=username,
                        defaults={
                            "email": email,
                        },
                    )
                )

                if user_created:
                    # Password sengaja tidak usable
                    # karena user benchmark tidak
                    # digunakan untuk login.
                    user.set_unusable_password()

                    user.save(
                        update_fields=[
                            "password"
                        ]
                    )

                # ==============================
                # EMPLOYEE
                # ==============================

                employee, employee_created = (
                    Employee.objects.get_or_create(
                        employee_code=employee_code,

                        defaults={
                            "user": user,

                            "full_name":
                                f"Benchmark Employee "
                                f"{number:04d}",

                            "job_title":
                                job_title,

                            "status":
                                "active",
                        },
                    )
                )

                if employee_created:
                    created_count += 1

                if number % 100 == 0:
                    self.stdout.write(
                        f"Progress employee: "
                        f"{number}/"
                        f"{self.TARGET_EMPLOYEES}"
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Employee baru dibuat: "
                    f"{created_count}"
                )
            )

        else:
            self.stdout.write(
                self.style.WARNING(
                    "Jumlah Employee sudah >= 1000. "
                    "Tidak membuat Employee baru."
                )
            )

        # ======================================
        # AMBIL 1000 EMPLOYEE PERTAMA
        # ======================================

        employees = list(
            Employee.objects
            .order_by("id")[:self.TARGET_EMPLOYEES]
        )

        if len(employees) < self.TARGET_EMPLOYEES:
            raise CommandError(
                f"Employee hanya {len(employees)}. "
                f"Target 1000 belum terpenuhi."
            )

        # ======================================
        # PAYROLL PROFILE
        # ======================================

        self.stdout.write("")
        self.stdout.write(
            "Membuat PayrollProfile..."
        )

        profile_created = 0

        for employee in employees:

            profile, created = (
                PayrollProfile.objects.get_or_create(
                    employee=employee,

                    defaults={
                        "ptkp_status":
                            "TK/0",

                        "bpjs_wage":
                            Decimal("10000000"),

                        "jkk_risk":
                            "LOW",

                        "bpjs_ketenagakerjaan_active":
                            True,

                        "bpjs_kesehatan_active":
                            True,
                    },
                )
            )

            if created:
                profile_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"PayrollProfile baru: "
                f"{profile_created}"
            )
        )

        # ======================================
        # SALARY COMPONENT
        # ======================================

        self.stdout.write("")
        self.stdout.write(
            "Membuat SalaryComponent..."
        )

        component_created = 0

        for employee in employees:

            component, created = (
                SalaryComponent.objects.get_or_create(
                    employee_id=employee.id,

                    name="Gaji Pokok",

                    defaults={
                        "component_type":
                            "earning",

                        "calculation_method":
                            "fixed",

                        "amount":
                            Decimal("10000000"),

                        "is_active":
                            True,
                    },
                )
            )

            if created:
                component_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"SalaryComponent baru: "
                f"{component_created}"
            )
        )

        # ======================================
        # HASIL AKHIR
        # ======================================

        employee_count = (
            Employee.objects.count()
        )

        profile_count = (
            PayrollProfile.objects.count()
        )

        component_count = (
            SalaryComponent.objects.count()
        )

        self.stdout.write("")
        self.stdout.write(
            "======================================"
        )
        self.stdout.write(
            "HASIL SEED"
        )
        self.stdout.write(
            "======================================"
        )

        self.stdout.write(
            f"Employee        : "
            f"{employee_count}"
        )

        self.stdout.write(
            f"PayrollProfile  : "
            f"{profile_count}"
        )

        self.stdout.write(
            f"SalaryComponent : "
            f"{component_count}"
        )

        self.stdout.write("")

        if profile_count >= 1000:
            self.stdout.write(
                self.style.SUCCESS(
                    "DATA BENCHMARK SIAP."
                )
            )

        else:
            self.stdout.write(
                self.style.ERROR(
                    "PayrollProfile belum mencapai 1000."
                )
            )
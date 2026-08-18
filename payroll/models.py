from django.db import models


# =========================================================
# SALARY COMPONENT
# PAY-01 - SUDAH ADA
# =========================================================

class SalaryComponent(models.Model):

    class ComponentType(models.TextChoices):
        EARNING = "earning", "Earning"
        DEDUCTION = "deduction", "Deduction"

    class CalculationMethod(models.TextChoices):
        FIXED = "fixed", "Fixed"
        ATTENDANCE = "attendance", "Attendance"

    # Sementara tetap mengikuti model Anda yang sebelumnya
    employee_id = models.BigIntegerField()

    component_type = models.CharField(
        max_length=20,
        choices=ComponentType.choices
    )

    name = models.CharField(
        max_length=100
    )

    calculation_method = models.CharField(
        max_length=20,
        choices=CalculationMethod.choices,
        default=CalculationMethod.FIXED
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    rate_per_day = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = "SalaryComponent"

    def __str__(self):
        return f"Employee {self.employee_id} - {self.name}"


# =========================================================
# PAYROLL PROFILE
# PAY-02
# =========================================================

class PayrollProfile(models.Model):

    class PTKPStatus(models.TextChoices):
        TK_0 = "TK/0", "TK/0"
        TK_1 = "TK/1", "TK/1"
        TK_2 = "TK/2", "TK/2"
        TK_3 = "TK/3", "TK/3"

        K_0 = "K/0", "K/0"
        K_1 = "K/1", "K/1"
        K_2 = "K/2", "K/2"
        K_3 = "K/3", "K/3"

    class JKKRisk(models.TextChoices):
        VERY_LOW = "VERY_LOW", "Sangat Rendah - 0.24%"
        LOW = "LOW", "Rendah - 0.54%"
        MEDIUM = "MEDIUM", "Sedang - 0.89%"
        HIGH = "HIGH", "Tinggi - 1.27%"
        VERY_HIGH = "VERY_HIGH", "Sangat Tinggi - 1.74%"

    employee = models.OneToOneField(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="payroll_profile",
    )

    ptkp_status = models.CharField(
        max_length=4,
        choices=PTKPStatus.choices,
        default=PTKPStatus.TK_0,
    )

    bpjs_wage = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    jkk_risk = models.CharField(
        max_length=20,
        choices=JKKRisk.choices,
        default=JKKRisk.LOW,
    )

    bpjs_ketenagakerjaan_active = models.BooleanField(
        default=True
    )

    bpjs_kesehatan_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.employee} - {self.ptkp_status}"


# =========================================================
# PAYROLL RUN
# PAY-02
# =========================================================

class PayrollRun(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("processing", "Processing"),
        ("completed", "Completed"),
    ]

    period_month = models.PositiveSmallIntegerField()

    period_year = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "PayrollRun"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "period_month",
                    "period_year",
                ],
                name="unique_payroll_period",
            )
        ]

    def __str__(self):
        return (
            f"Payroll "
            f"{self.period_month}/"
            f"{self.period_year}"
        )


# =========================================================
# PAYSLIP
# PAY-02
# =========================================================

class Payslip(models.Model):

    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="payslips",
    )

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="payslips",
    )

    gross_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    pph21_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    bpjs_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    total_deduction = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    net_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    pdf_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    bank_account_no = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    calculation_detail = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = "Payslip"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "payroll_run",
                    "employee",
                ],
                name="unique_payslip_payroll_employee",
            )
        ]

    def __str__(self):
        return (
            f"Payslip {self.employee} - "
            f"{self.payroll_run.period_month}/"
            f"{self.payroll_run.period_year}"
        )
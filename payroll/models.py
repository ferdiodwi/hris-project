from django.db import models


class SalaryComponent(models.Model):

    class ComponentType(models.TextChoices):
        EARNING = "earning", "Earning"
        DEDUCTION = "deduction", "Deduction"

    class CalculationMethod(models.TextChoices):
        FIXED = "fixed", "Fixed"
        ATTENDANCE = "attendance", "Attendance"

    # Sementara belum ForeignKey karena model Employee belum ada
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
from django.core.validators import MinValueValidator
from django.db import models


class ShiftMaster(models.Model):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        max_length=50,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    tolerance_minutes = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    class Meta:
        db_table = "ShiftMaster"

    def __str__(self):
        return self.name


class ShiftRoster(models.Model):
    id = models.BigAutoField(primary_key=True)

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="shift_rosters",
    )

    shift_master = models.ForeignKey(
        ShiftMaster,
        on_delete=models.RESTRICT,
        db_column="shift_master_id",
        related_name="rosters",
    )

    date = models.DateField()

    class Meta:
        db_table = "ShiftRoster"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "employee",
                    "date",
                ],
                name="uq_roster_employee_date",
            ),
        ]

        indexes = [
            models.Index(
                fields=["shift_master"],
                name="idx_roster_shift",
            ),
        ]

    def __str__(self):
        return (
            f"Employee {self.employee_id} - "
            f"Shift {self.shift_master_id} - "
            f"{self.date}"
        )
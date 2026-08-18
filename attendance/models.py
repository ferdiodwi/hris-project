from django.db import models


class AttendanceLog(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="attendance_logs",
    )

    roster = models.ForeignKey(
        "shifting.ShiftRoster",
        on_delete=models.SET_NULL,
        db_column="roster_id",
        related_name="attendance_logs",
        null=True,
        blank=True,
    )

    clock_in_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    clock_out_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    clock_in_lat = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )

    clock_in_lng = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )

    clock_in_photo_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        default="present",
    )

    class Meta:
        db_table = "AttendanceLog"

        indexes = [
            models.Index(
                fields=["employee"],
                name="idx_attendance_employee",
            ),
            models.Index(
                fields=["roster"],
                name="idx_attendance_roster",
            ),
        ]

    def __str__(self):
        return (
            f"Employee {self.employee_id} - "
            f"{self.clock_in_time} - "
            f"{self.status}"
        )
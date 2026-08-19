from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class KpiGoal(models.Model):

    class PeriodType(models.TextChoices):
        QUARTERLY = "QUARTERLY", "Quarterly"
        YEARLY = "YEARLY", "Yearly"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="kpi_goals",
        db_column="employee_id",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    period_type = models.CharField(
        max_length=20,
        choices=PeriodType.choices,
    )

    year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(2100),
        ],
    )

    quarter = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ],
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01),
            MaxValueValidator(100),
        ],
    )

    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )

    unit = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    approved_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        related_name="approved_kpi_goals",
        null=True,
        blank=True,
        db_column="approved_by_id",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "KpiGoal"
        ordering = [
            "-year",
            "-quarter",
            "-created_at",
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_code} - "
            f"{self.title}"
        )

class KpiAppraisal(models.Model):

    class AppraisalType(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        PEER = "PEER", "Peer"
        SELF = "SELF", "Self"

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="received_kpi_appraisals",
        db_column="employee_id",
    )

    reviewer = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="submitted_kpi_appraisals",
        db_column="reviewer_id",
    )

    appraisal_type = models.CharField(
        max_length=20,
        choices=AppraisalType.choices,
    )

    period_type = models.CharField(
        max_length=20,
        choices=KpiGoal.PeriodType.choices,
    )

    year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(2100),
        ],
    )

    quarter = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ],
    )

    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    comment = models.TextField(
        blank=True,
        default="",
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "KpiAppraisal"

        ordering = [
            "-year",
            "-quarter",
            "-submitted_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "employee",
                    "year",
                    "period_type",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.employee.employee_code} - "
            f"{self.appraisal_type} - "
            f"{self.score}"
        )

class KpiTask(models.Model):

    class Status(models.TextChoices):
        TODO = "TODO", "To-Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    goal = models.ForeignKey(
        KpiGoal,
        on_delete=models.CASCADE,
        related_name="tasks",
        db_column="goal_id",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_kpi_tasks",
        db_column="created_by_id",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "KpiTask"

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "goal",
                    "status",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.goal.employee.employee_code} - "
            f"{self.title} - "
            f"{self.status}"
        )
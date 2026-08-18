from django.db import models


class ApprovalRequest(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="approval_requests",
    )

    request_type = models.CharField(
        max_length=30
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    attachment_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )

    reason = models.TextField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        default="pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = "ApprovalRequest"

        indexes = [
            models.Index(
                fields=["employee"],
                name="idx_apprequest_employee",
            ),
        ]

    def __str__(self):
        return (
            f"{self.employee_id} - "
            f"{self.request_type} - "
            f"{self.status}"
        )


class ApprovalStep(models.Model):
    id = models.BigAutoField(
        primary_key=True
    )

    request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        db_column="request_id",
        related_name="approval_steps",
    )

    approver = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.RESTRICT,
        db_column="approver_id",
        related_name="approval_steps",
    )

    level = models.IntegerField(
        default=1
    )

    decision = models.CharField(
        max_length=20,
        default="pending",
    )

    decided_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    note = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "ApprovalStep"

        indexes = [
            models.Index(
                fields=["request"],
                name="idx_appstep_request",
            ),
            models.Index(
                fields=["approver"],
                name="idx_appstep_approver",
            ),
        ]

    def __str__(self):
        return (
            f"Request {self.request_id} - "
            f"Level {self.level} - "
            f"{self.decision}"
        )
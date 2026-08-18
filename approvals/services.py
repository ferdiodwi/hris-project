from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from accounts.models import Employee

from uam.models import UserRole

from .models import (
    ApprovalRequest,
    ApprovalStep,
)


HR_ROLE_NAME = "HR"


def get_employee_from_user(
    user,
):
    try:
        return (
            Employee.objects
            .select_related(
                "reports_to"
            )
            .get(
                user_id=user.id
            )
        )

    except Employee.DoesNotExist:
        raise ValidationError(
            {
                "employee": [
                    (
                        "User ini belum memiliki "
                        "data Employee."
                    )
                ]
            }
        )


def is_hr_user(
    user,
):
    return UserRole.objects.filter(
        user_id=user.id,
        role__name__iexact=HR_ROLE_NAME,
    ).exists()


def create_initial_approval_step(
    approval_request,
):
    employee = (
        Employee.objects
        .select_related(
            "reports_to"
        )
        .get(
            pk=approval_request.employee_id
        )
    )

    if employee.reports_to_id is None:
        # Tidak ada reporting line.
        # Request tetap pending dan
        # nantinya masih dapat diproses HR.
        return None

    return ApprovalStep.objects.create(
        request=approval_request,
        approver_id=employee.reports_to_id,
        level=1,
        decision="pending",
    )


def process_approval_decision(
    user,
    request_id,
    decision,
    note=None,
):
    if decision not in [
        "approved",
        "rejected",
    ]:
        raise ValidationError(
            {
                "decision": [
                    "Decision tidak valid."
                ]
            }
        )

    actor = get_employee_from_user(
        user
    )

    actor_is_hr = is_hr_user(
        user
    )

    with transaction.atomic():

        try:
            approval_request = (
                ApprovalRequest.objects
                .select_for_update()
                .select_related(
                    "employee"
                )
                .get(
                    pk=request_id
                )
            )

        except ApprovalRequest.DoesNotExist:
            raise ValidationError(
                {
                    "request": [
                        (
                            "Approval request "
                            "tidak ditemukan."
                        )
                    ]
                }
            )

        if approval_request.status != "pending":
            raise ValidationError(
                {
                    "request": [
                        (
                            "Approval request ini "
                            "sudah selesai diproses."
                        )
                    ]
                }
            )

        current_step = (
            ApprovalStep.objects
            .select_for_update()
            .select_related(
                "approver",
                "approver__reports_to",
            )
            .filter(
                request_id=request_id,
                decision="pending",
            )
            .order_by(
                "level",
                "id",
            )
            .first()
        )

        # Jika requester tidak punya reports_to,
        # HR tetap boleh memproses request.
        if current_step is None:

            if not actor_is_hr:
                raise PermissionDenied(
                    (
                        "Tidak ada approval step "
                        "untuk user ini."
                    )
                )

            last_step = (
                ApprovalStep.objects
                .filter(
                    request_id=request_id
                )
                .order_by(
                    "-level"
                )
                .first()
            )

            next_level = (
                last_step.level + 1
                if last_step
                else 1
            )

            current_step = (
                ApprovalStep.objects.create(
                    request=approval_request,
                    approver=actor,
                    level=next_level,
                    decision="pending",
                )
            )

        # Line manager sesuai ApprovalStep
        # atau HR boleh memproses.
        if (
            current_step.approver_id
            != actor.id
            and not actor_is_hr
        ):
            raise PermissionDenied(
                (
                    "Anda bukan approver "
                    "untuk request ini."
                )
            )

        current_step.decision = decision

        current_step.decided_at = (
            timezone.now()
        )

        current_step.note = note

        current_step.save(
            update_fields=[
                "decision",
                "decided_at",
                "note",
            ]
        )

        # Reject langsung mengakhiri
        # keseluruhan request.
        if decision == "rejected":

            approval_request.status = (
                "rejected"
            )

            approval_request.save(
                update_fields=[
                    "status"
                ]
            )

            return {
                "request": approval_request,
                "processed_step": current_step,
                "next_step": None,
            }

        # APPROVE:
        # cari reporting line berikutnya
        # dari approver pada step saat ini.
        step_approver = (
            Employee.objects
            .select_related(
                "reports_to"
            )
            .get(
                pk=current_step.approver_id
            )
        )

        next_approver_id = (
            step_approver.reports_to_id
        )

        next_step = None

        if next_approver_id:

            next_step = (
                ApprovalStep.objects.create(
                    request=approval_request,
                    approver_id=(
                        next_approver_id
                    ),
                    level=(
                        current_step.level
                        + 1
                    ),
                    decision="pending",
                )
            )

            # Masih ada level berikutnya.
            approval_request.status = (
                "pending"
            )

            approval_request.save(
                update_fields=[
                    "status"
                ]
            )

        else:
            # Tidak ada atasan lagi.
            # Semua level selesai.
            approval_request.status = (
                "approved"
            )

            approval_request.save(
                update_fields=[
                    "status"
                ]
            )

        return {
            "request": approval_request,
            "processed_step": current_step,
            "next_step": next_step,
        }
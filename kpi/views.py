from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Employee

from .models import KpiGoal
from .serializers import (
    KpiGoalSerializer,
    KpiGoalSetTargetSerializer,
)


class KpiGoalViewSet(ModelViewSet):

    serializer_class = KpiGoalSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_current_employee(self):

        try:
            return Employee.objects.get(
                user=self.request.user
            )

        except Employee.DoesNotExist:
            raise PermissionDenied(
                "User login tidak memiliki "
                "data Employee."
            )

    def get_queryset(self):

        current_employee = (
            self.get_current_employee()
        )

        return (
            KpiGoal.objects
            .select_related(
                "employee",
                "approved_by",
            )
            .filter(
                Q(
                    employee=current_employee
                )
                |
                Q(
                    employee__reports_to=(
                        current_employee
                    )
                )
            )
            .distinct()
        )

    def perform_create(
        self,
        serializer,
    ):

        employee = (
            self.get_current_employee()
        )

        serializer.save(
            employee=employee
        )

    def perform_update(
        self,
        serializer,
    ):

        current_employee = (
            self.get_current_employee()
        )

        goal = serializer.instance

        is_owner = (
            goal.employee_id
            == current_employee.id
        )

        is_manager = (
            goal.employee.reports_to_id
            == current_employee.id
        )

        if not is_owner and not is_manager:
            raise PermissionDenied(
                "Anda tidak memiliki akses "
                "untuk mengubah goal ini."
            )

        if (
            is_owner
            and goal.status
            == KpiGoal.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Goal yang sudah APPROVED "
                        "tidak dapat diubah "
                        "oleh karyawan."
                    )
                }
            )

        serializer.save()

    def perform_destroy(
        self,
        instance,
    ):

        current_employee = (
            self.get_current_employee()
        )

        is_owner = (
            instance.employee_id
            == current_employee.id
        )

        is_manager = (
            instance.employee.reports_to_id
            == current_employee.id
        )

        if not is_owner and not is_manager:
            raise PermissionDenied(
                "Anda tidak memiliki akses "
                "untuk menghapus goal ini."
            )

        if (
            is_owner
            and instance.status
            == KpiGoal.Status.APPROVED
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Goal yang sudah APPROVED "
                        "tidak dapat dihapus "
                        "oleh karyawan."
                    )
                }
            )

        instance.delete()

    @action(
        detail=True,
        methods=["patch"],
        url_path="set-target",
    )
    def set_target(
        self,
        request,
        pk=None,
    ):

        goal = self.get_object()

        manager = (
            self.get_current_employee()
        )

        if (
            goal.employee.reports_to_id
            != manager.id
        ):
            raise PermissionDenied(
                "Hanya manager langsung "
                "karyawan yang dapat "
                "menentukan target."
            )

        serializer = (
            KpiGoalSetTargetSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        goal.target_value = (
            serializer.validated_data[
                "target_value"
            ]
        )

        goal.save(
            update_fields=[
                "target_value",
                "updated_at",
            ]
        )

        return Response(
            KpiGoalSerializer(
                goal
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(
        self,
        request,
        pk=None,
    ):

        goal = self.get_object()

        manager = (
            self.get_current_employee()
        )

        if (
            goal.employee.reports_to_id
            != manager.id
        ):
            raise PermissionDenied(
                "Hanya manager langsung "
                "karyawan yang dapat "
                "approve goal."
            )

        if goal.target_value is None:
            raise ValidationError(
                {
                    "target_value": (
                        "Manager harus "
                        "menentukan target "
                        "sebelum approve."
                    )
                }
            )

        goal.status = (
            KpiGoal.Status.APPROVED
        )

        goal.approved_by = manager

        goal.approved_at = timezone.now()

        goal.save(
            update_fields=[
                "status",
                "approved_by",
                "approved_at",
                "updated_at",
            ]
        )

        return Response(
            KpiGoalSerializer(
                goal
            ).data,
            status=status.HTTP_200_OK,
        )
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from django.db.models import (
    Avg,
    Count,
    Q,
)

from django.shortcuts import (
    get_object_or_404,
)

from rest_framework import (
    mixins,
    status,
)

from rest_framework.decorators import (
    action,
)

from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import (
    Response,
)

from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
)

from .models import (
    KpiAppraisal,
    KpiGoal,
    KpiTask,
)

from .serializers import (
    KpiAppraisalSerializer,
    KpiFinalScoreQuerySerializer,
    KpiGoalSerializer,
    KpiGoalSetTargetSerializer,
    KpiTaskSerializer,
    KpiTaskStatusSerializer,
)

from accounts.models import Employee

from django.utils import timezone


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

class KpiAppraisalViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):

    serializer_class = KpiAppraisalSerializer

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
            KpiAppraisal.objects
            .select_related(
                "employee",
                "reviewer",
            )
            .filter(
                Q(
                    employee=current_employee
                )
                |
                Q(
                    reviewer=current_employee
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
        reviewer = (
            self.get_current_employee()
        )

        employee = (
            serializer.validated_data[
                "employee"
            ]
        )

        appraisal_type = (
            serializer.validated_data[
                "appraisal_type"
            ]
        )

        period_type = (
            serializer.validated_data[
                "period_type"
            ]
        )

        year = (
            serializer.validated_data[
                "year"
            ]
        )

        quarter = (
            serializer.validated_data.get(
                "quarter"
            )
        )

        # SELF
        if (
            appraisal_type
            == KpiAppraisal.AppraisalType.SELF
        ):
            if employee.id != reviewer.id:
                raise PermissionDenied(
                    "SELF appraisal hanya dapat "
                    "dilakukan untuk diri sendiri."
                )

        # MANAGER
        elif (
            appraisal_type
            == KpiAppraisal.AppraisalType.MANAGER
        ):
            if (
                employee.reports_to_id
                != reviewer.id
            ):
                raise PermissionDenied(
                    "MANAGER appraisal hanya "
                    "dapat dilakukan oleh "
                    "manager langsung karyawan."
                )

        # PEER
        elif (
            appraisal_type
            == KpiAppraisal.AppraisalType.PEER
        ):
            if employee.id == reviewer.id:
                raise PermissionDenied(
                    "PEER appraisal tidak dapat "
                    "dilakukan untuk diri sendiri."
                )

            reviewer_is_manager = (
                employee.reports_to_id
                == reviewer.id
            )

            employee_is_manager = (
                reviewer.reports_to_id
                == employee.id
            )

            if (
                reviewer_is_manager
                or employee_is_manager
            ):
                raise PermissionDenied(
                    "Hubungan manager dan "
                    "direct subordinate bukan "
                    "PEER appraisal."
                )

        duplicate = (
            KpiAppraisal.objects.filter(
                employee=employee,
                reviewer=reviewer,
                appraisal_type=appraisal_type,
                period_type=period_type,
                year=year,
                quarter=quarter,
            ).exists()
        )

        if duplicate:
            raise ValidationError(
                {
                    "detail": (
                        "Reviewer sudah "
                        "mengirim appraisal "
                        "untuk employee, tipe, "
                        "dan periode ini."
                    )
                }
            )

        serializer.save(
            reviewer=reviewer
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="final-score",
    )
    def final_score(
        self,
        request,
    ):
        query = (
            KpiFinalScoreQuerySerializer(
                data=request.query_params
            )
        )

        query.is_valid(
            raise_exception=True
        )

        data = query.validated_data

        current_employee = (
            self.get_current_employee()
        )

        employee = get_object_or_404(
            Employee,
            id=data["employee_id"],
        )

        is_self = (
            employee.id
            == current_employee.id
        )

        is_manager = (
            employee.reports_to_id
            == current_employee.id
        )

        if (
            not is_self
            and not is_manager
        ):
            raise PermissionDenied(
                "Final score hanya dapat "
                "dilihat oleh karyawan "
                "bersangkutan atau "
                "manager langsungnya."
            )

        appraisals = (
            KpiAppraisal.objects.filter(
                employee=employee,
                period_type=(
                    data["period_type"]
                ),
                year=data["year"],
                quarter=data["quarter"],
            )
        )

        grouped = (
            appraisals
            .values(
                "appraisal_type"
            )
            .annotate(
                average_score=Avg(
                    "score"
                ),
                reviewer_count=Count(
                    "id"
                ),
            )
        )

        grouped = list(grouped)

        if not grouped:
            raise ValidationError(
                {
                    "detail": (
                        "Belum ada appraisal "
                        "untuk periode tersebut."
                    )
                }
            )

        weights = {
            KpiAppraisal.AppraisalType.MANAGER:
                data["manager_weight"],

            KpiAppraisal.AppraisalType.PEER:
                data["peer_weight"],

            KpiAppraisal.AppraisalType.SELF:
                data["self_weight"],
        }

        numerator = Decimal("0")
        denominator = Decimal("0")

        breakdown = {}

        for item in grouped:
            appraisal_type = (
                item["appraisal_type"]
            )

            average_score = Decimal(
                str(
                    item["average_score"]
                )
            )

            weight = weights[
                appraisal_type
            ]

            breakdown[
                appraisal_type
            ] = {
                "average_score": str(
                    average_score.quantize(
                        Decimal("0.01")
                    )
                ),
                "reviewer_count": (
                    item[
                        "reviewer_count"
                    ]
                ),
                "weight": str(
                    weight
                ),
            }

            if weight > 0:
                numerator += (
                    average_score
                    * weight
                )

                denominator += weight

        if denominator <= 0:
            raise ValidationError(
                {
                    "detail": (
                        "Tidak ada weight aktif "
                        "untuk appraisal yang "
                        "tersedia."
                    )
                }
            )

        final_score = (
            numerator
            / denominator
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        return Response(
            {
                "employee_id": (
                    employee.id
                ),
                "employee_code": (
                    employee.employee_code
                ),
                "employee_name": (
                    employee.full_name
                ),
                "period_type": (
                    data["period_type"]
                ),
                "year": data["year"],
                "quarter": (
                    data["quarter"]
                ),
                "breakdown": breakdown,
                "final_score": str(
                    final_score
                ),
            },
            status=status.HTTP_200_OK,
        )

class KpiTaskViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):

    serializer_class = KpiTaskSerializer

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

        queryset = (
            KpiTask.objects
            .select_related(
                "goal",
                "goal__employee",
                "created_by",
            )
            .filter(
                Q(
                    goal__employee=(
                        current_employee
                    )
                )
                |
                Q(
                    goal__employee__reports_to=(
                        current_employee
                    )
                )
            )
            .distinct()
        )

        status_filter = (
            self.request.query_params.get(
                "status"
            )
        )

        if status_filter:
            if (
                status_filter
                not in KpiTask.Status.values
            ):
                raise ValidationError(
                    {
                        "status": (
                            "Status harus TODO, "
                            "IN_PROGRESS, atau DONE."
                        )
                    }
                )

            queryset = queryset.filter(
                status=status_filter
            )

        goal_id = (
            self.request.query_params.get(
                "goal_id"
            )
        )

        if goal_id:
            queryset = queryset.filter(
                goal_id=goal_id
            )

        return queryset
        
    def perform_create(
        self,
        serializer,
    ):
        creator = (
            self.get_current_employee()
        )

        goal = (
            serializer.validated_data[
                "goal"
            ]
        )

        goal_owner = goal.employee

        is_owner = (
            goal_owner.id
            == creator.id
        )

        is_direct_manager = (
            goal_owner.reports_to_id
            == creator.id
        )

        if (
            not is_owner
            and not is_direct_manager
        ):
            raise PermissionDenied(
                "Task hanya dapat dibuat "
                "oleh pemilik goal atau "
                "manager langsungnya."
            )

        serializer.save(
            created_by=creator
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
    )
    def update_status(
        self,
        request,
        pk=None,
    ):
        task = self.get_object()

        current_employee = (
            self.get_current_employee()
        )

        if (
            task.goal.employee_id
            != current_employee.id
        ):
            raise PermissionDenied(
                "Status task hanya dapat "
                "diubah oleh pemilik task."
            )

        serializer = (
            KpiTaskStatusSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        task.status = (
            serializer.validated_data[
                "status"
            ]
        )

        task.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            KpiTaskSerializer(
                task
            ).data,
            status=status.HTTP_200_OK,
        )


    @action(

        detail=False,
        methods=["get"],
        url_path="monitor",
    )

    def monitor(
        self,
        request,
    ):
        manager = (
            self.get_current_employee()
        )

        tasks = (
            KpiTask.objects
            .select_related(
                "goal",
                "goal__employee",
                "created_by",
            )
            .filter(
                goal__employee__reports_to=(
                    manager
                )
            )
        )

        total = tasks.count()

        todo = tasks.filter(
            status=KpiTask.Status.TODO
        ).count()

        in_progress = tasks.filter(
            status=(
                KpiTask.Status.IN_PROGRESS
            )
        ).count()

        done = tasks.filter(
            status=KpiTask.Status.DONE
        ).count()

        if total > 0:
            progress_percent = (
                Decimal(done)
                / Decimal(total)
                * Decimal("100")
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

        else:
            progress_percent = (
                Decimal("0.00")
            )

        return Response(
            {
                "summary": {
                    "total": total,
                    "todo": todo,
                    "in_progress": (
                        in_progress
                    ),
                    "done": done,
                    "progress_percent": str(
                        progress_percent
                    ),
                },
                "tasks": (
                    KpiTaskSerializer(
                        tasks,
                        many=True,
                    ).data
                ),
            },
            status=status.HTTP_200_OK,
        )
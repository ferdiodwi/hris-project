from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SalaryComponent

from .serializers import (
    MealAllowanceCalculationSerializer,
    SalaryComponentSerializer,
)

from .services.attendance_service import (
    get_attendance_days,
)


class SalaryComponentViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryComponentSerializer

    def get_queryset(self):
        queryset = (
            SalaryComponent.objects
            .all()
            .order_by("id")
        )

        employee_id = (
            self.request.query_params.get(
                "employee_id"
            )
        )

        component_type = (
            self.request.query_params.get(
                "component_type"
            )
        )

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        if component_type:
            queryset = queryset.filter(
                component_type=component_type
            )

        return queryset

    @action(
        detail=True,
        methods=["post"],
        url_path="calculate-attendance",
    )
    def calculate_attendance(
        self,
        request,
        pk=None,
    ):
        component = self.get_object()

        if (
            component.calculation_method
            != SalaryComponent.CalculationMethod.ATTENDANCE
        ):
            return Response(
                {
                    "message":
                        "Komponen ini bukan berbasis attendance."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = (
            MealAllowanceCalculationSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        month = (
            serializer.validated_data["month"]
        )

        year = (
            serializer.validated_data["year"]
        )

        attendance_days = get_attendance_days(
            employee_id=component.employee_id,
            month=month,
            year=year,
        )

        rate_per_day = (
            component.rate_per_day
            or Decimal("0")
        )

        total_amount = (
            Decimal(attendance_days)
            * rate_per_day
        )

        return Response(
            {
                "employee_id":
                    component.employee_id,

                "salary_component_id":
                    component.id,

                "component_name":
                    component.name,

                "component_type":
                    component.component_type,

                "calculation_method":
                    component.calculation_method,

                "month":
                    month,

                "year":
                    year,

                "attendance_days":
                    attendance_days,

                "rate_per_day":
                    rate_per_day,

                "total_amount":
                    total_amount,
            },

            status=status.HTTP_200_OK,
        )
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SalaryComponent

from .models import (
    PayrollProfile,
    PayrollRun,
    Payslip,
)

from .serializers import (
    MealAllowanceCalculationSerializer,
    SalaryComponentSerializer,
    PayrollProfileSerializer,
    PayrollRunPay02Serializer,
    PayslipPay02Serializer,
)

from .services.payroll_service import (
    process_payroll_run,
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

class PayrollProfileListCreateView(
    generics.ListCreateAPIView
):
    queryset = (
        PayrollProfile.objects
        .select_related("employee")
        .all()
    )

    serializer_class = (
        PayrollProfileSerializer
    )


class PayrollRunPay02ListCreateView(
    generics.ListCreateAPIView
):
    queryset = (
        PayrollRun.objects
        .all()
        .order_by(
            "-period_year",
            "-period_month",
        )
    )

    serializer_class = (
        PayrollRunPay02Serializer
    )


class ProcessPayrollRunPay02View(
    APIView
):
    def post(
        self,
        request,
        pk,
    ):
        payroll_run = get_object_or_404(
            PayrollRun,
            pk=pk,
        )

        if payroll_run.status == "processing":

            return Response(
                {
                    "detail":
                    "Payroll sedang diproses."
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:

            total_employee = (
                process_payroll_run(
                    payroll_run
                )
            )

        except ValueError as error:

            return Response(
                {
                    "detail":
                    str(error)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as error:

            return Response(
                {
                    "detail":
                    str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message":
                    "Payroll PAY-02 berhasil diproses.",

                "payroll_run_id":
                    payroll_run.id,

                "total_employee":
                    total_employee,

                "status":
                    "completed",
            },
            status=status.HTTP_200_OK,
        )


class PayrollRunPayslipPay02ListView(
    generics.ListAPIView
):
    serializer_class = (
        PayslipPay02Serializer
    )

    def get_queryset(self):

        return (
            Payslip.objects
            .filter(
                payroll_run_id=(
                    self.kwargs[
                        "run_id"
                    ]
                )
            )
            .select_related(
                "employee",
                "payroll_run",
            )
            .order_by(
                "employee_id"
            )
        )
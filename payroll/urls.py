from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    SalaryComponentViewSet,
    PayrollProfileListCreateView,
    PayrollRunPay02ListCreateView,
    ProcessPayrollRunPay02View,
    PayrollRunPayslipPay02ListView,
)


router = DefaultRouter()

router.register(
    r"salary-components",
    SalaryComponentViewSet,
    basename="salary-component"
)


urlpatterns = [
    path("", include(router.urls)),

    path(
        "pay02/profiles/",
        PayrollProfileListCreateView.as_view(),
        name="pay02-profile-list",
    ),

    path(
        "pay02/runs/",
        PayrollRunPay02ListCreateView.as_view(),
        name="pay02-run-list",
    ),

    path(
    "pay02/runs/<int:pk>/process/",
    ProcessPayrollRunPay02View.as_view(),
    name="pay02-run-process",
),

    path(
    "pay02/runs/<int:run_id>/payslips/",
    PayrollRunPayslipPay02ListView.as_view(),
    name="pay02-payslip-list",
),
]
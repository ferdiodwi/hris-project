from django.urls import path

from .pay03_views import (
    DownloadPayslipPDFView,
    GeneratePayslipPDFView,
    PayrollBankCSVView,
    PayrollRunProcessView,
)


urlpatterns = [
    path(
        "payroll-runs/<int:pk>/process/",
        PayrollRunProcessView.as_view(),
    ),

    path(
        "payslips/<int:pk>/generate-pdf/",
        GeneratePayslipPDFView.as_view(),
    ),

    path(
        "payslips/<int:pk>/download/",
        DownloadPayslipPDFView.as_view(),
    ),

    path(
        "payroll-runs/<int:pk>/bank-file/",
        PayrollBankCSVView.as_view(),
    ),
]
from pathlib import Path

from django.http import (
    FileResponse,
    HttpResponse,
)

from django.shortcuts import (
    get_object_or_404,
)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from payroll.models import (
    PayrollRun,
    Payslip,
)

from payroll.services.bank_file_service import (
    generate_bank_csv,
)

from payroll.services.payroll_service import (
    process_payroll_run,
)

from payroll.services.payslip_pdf_service import (
    generate_payslip_pdf,
)


class PayrollRunProcessView(APIView):

    def post(
        self,
        request,
        pk,
    ):

        payroll_run = get_object_or_404(
            PayrollRun,
            pk=pk,
        )

        try:
            total = process_payroll_run(
                payroll_run
            )

        except Exception as error:
            return Response(
                {
                    "detail":
                    str(error)
                },
                status=(
                    status
                    .HTTP_400_BAD_REQUEST
                ),
            )

        return Response({
            "message":
                "Payroll berhasil diproses.",

            "payroll_run_id":
                payroll_run.id,

            "total_employee":
                total,

            "status":
                "completed",
        })


class GeneratePayslipPDFView(APIView):

    def post(
        self,
        request,
        pk,
    ):

        payslip = get_object_or_404(
            Payslip.objects.select_related(
                "employee",
                "payroll_run",
            ),
            pk=pk,
        )

        result = generate_payslip_pdf(
            payslip
        )

        # Password ditampilkan saat generate
        # untuk kebutuhan testing.
        return Response({
            "message":
                "PDF berhasil dibuat.",

            "payslip_id":
                payslip.id,

            "pdf_url":
                result["url"],

            "password":
                result["password"],
        })


class DownloadPayslipPDFView(APIView):

    def get(
        self,
        request,
        pk,
    ):

        payslip = get_object_or_404(
            Payslip,
            pk=pk,
        )

        if not payslip.pdf_url:

            return Response(
                {
                    "detail":
                    "PDF belum dibuat."
                },
                status=404,
            )

        from django.conf import settings

        relative = (
            payslip.pdf_url
            .replace(
                settings.MEDIA_URL,
                "",
                1,
            )
        )

        path = (
            Path(settings.MEDIA_ROOT)
            / relative
        )

        if not path.exists():

            return Response(
                {
                    "detail":
                    "File PDF tidak ditemukan."
                },
                status=404,
            )

        return FileResponse(
            open(path, "rb"),

            content_type=(
                "application/pdf"
            ),

            as_attachment=True,

            filename=path.name,
        )


class PayrollBankCSVView(APIView):

    def get(
        self,
        request,
        pk,
    ):

        payroll_run = get_object_or_404(
            PayrollRun,
            pk=pk,
        )

        try:
            csv_data = (
                generate_bank_csv(
                    payroll_run
                )
            )

        except ValueError as error:

            return Response(
                {
                    "detail":
                    str(error)
                },
                status=400,
            )

        response = HttpResponse(
            csv_data,
            content_type=(
                "text/csv; charset=utf-8"
            ),
        )

        response[
            "Content-Disposition"
        ] = (
            f'attachment; filename="'
            f'payroll_'
            f'{payroll_run.period_month}_'
            f'{payroll_run.period_year}.csv"'
        )

        return response
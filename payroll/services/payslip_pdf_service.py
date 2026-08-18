import secrets

from io import BytesIO
from pathlib import Path

from django.conf import settings

from pypdf import (
    PdfReader,
    PdfWriter,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
)
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def rupiah(value):
    value = int(value or 0)

    return (
        "Rp "
        + f"{value:,}"
        .replace(",", ".")
    )


def generate_pdf_password():
    return secrets.token_urlsafe(10)


def generate_payslip_pdf(payslip):

    raw_pdf = BytesIO()

    doc = SimpleDocTemplate(
        raw_pdf,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>SLIP GAJI KARYAWAN</b>",
            styles["Title"],
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    employee = payslip.employee

    payroll_run = payslip.payroll_run

    employee_data = [
        [
            "Nama",
            employee.full_name,
        ],
        [
            "Employee Code",
            employee.employee_code,
        ],
        [
            "Periode",
            (
                f"{payroll_run.period_month}/"
                f"{payroll_run.period_year}"
            ),
        ],
    ]

    employee_table = Table(
        employee_data,
        colWidths=[130, 350],
    )

    employee_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey,
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
        ])
    )

    elements.append(
        employee_table
    )

    elements.append(
        Spacer(1, 20)
    )

    salary_data = [
        [
            "Komponen",
            "Nominal",
        ],
        [
            "Gross Salary",
            rupiah(
                payslip.gross_salary
            ),
        ],
        [
            "PPh 21",
            rupiah(
                payslip.pph21_amount
            ),
        ],
        [
            "BPJS",
            rupiah(
                payslip.bpjs_amount
            ),
        ],
        [
            "Total Deduction",
            rupiah(
                payslip.total_deduction
            ),
        ],
        [
            "NET SALARY",
            rupiah(
                payslip.net_salary
            ),
        ],
    ]

    salary_table = Table(
        salary_data,
        colWidths=[240, 240],
    )

    salary_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey,
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "RIGHT",
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
        ])
    )

    elements.append(
        salary_table
    )

    doc.build(elements)

    raw_pdf.seek(0)

    # ================================
    # PASSWORD PROTECT
    # ================================

    password = generate_pdf_password()

    reader = PdfReader(
        raw_pdf
    )

    writer = PdfWriter(
        clone_from=reader
    )

    writer.encrypt(
        password,
        algorithm="AES-256-R5",
    )

    # ================================
    # FILE PATH
    # ================================

    relative_dir = Path(
        "payslips"
    ) / str(
        payroll_run.period_year
    ) / str(
        payroll_run.period_month
    )

    absolute_dir = (
        Path(settings.MEDIA_ROOT)
        / relative_dir
    )

    absolute_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"payslip_{payslip.id}.pdf"
    )

    absolute_path = (
        absolute_dir / filename
    )

    with open(
        absolute_path,
        "wb",
    ) as pdf_file:

        writer.write(
            pdf_file
        )

    relative_path = (
        relative_dir / filename
    )

    payslip.pdf_url = (
        settings.MEDIA_URL
        + relative_path.as_posix()
    )

    payslip.pdf_password = (
        password
    )

    payslip.save(
        update_fields=[
            "pdf_url",
            "pdf_password",
        ]
    )

    return {
        "path": absolute_path,
        "url": payslip.pdf_url,
        "password": password,
    }
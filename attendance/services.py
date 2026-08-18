from calendar import monthrange

from datetime import (
    date,
    datetime,
    timedelta,
)

from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from accounts.models import Employee

from shifting.models import ShiftRoster

from .models import AttendanceLog


def get_employee_from_user(user):
    try:
        return (
            Employee.objects
            .only("id")
            .get(user_id=user.id)
        )

    except Employee.DoesNotExist:
        raise serializers.ValidationError(
            {
                "employee": (
                    "User ini tidak memiliki "
                    "data Employee."
                )
            }
        )


def make_shift_datetime(
    roster_date,
    shift_time,
):
    value = datetime.combine(
        roster_date,
        shift_time,
    )

    if timezone.is_naive(value):
        value = timezone.make_aware(
            value,
            timezone.get_current_timezone(),
        )

    return value


def normalize_datetime(value):
    if value is None:
        return None

    if timezone.is_naive(value):
        value = timezone.make_aware(
            value,
            timezone.get_current_timezone(),
        )

    return timezone.localtime(value)


# =========================================================
# ATT-01
# CLOCK IN
# =========================================================

def clock_in_employee(
    user,
    lat,
    lng,
    photo_url,
):
    employee = get_employee_from_user(
        user
    )

    now = timezone.now()

    today = timezone.localdate()

    with transaction.atomic():

        roster = (
            ShiftRoster.objects
            .select_for_update()
            .select_related(
                "shift_master"
            )
            .filter(
                employee_id=employee.id,
                date=today,
            )
            .first()
        )

        if roster is None:
            raise serializers.ValidationError(
                {
                    "roster": (
                        "Tidak ada jadwal shift "
                        "untuk hari ini."
                    )
                }
            )

        existing_attendance = (
            AttendanceLog.objects
            .filter(
                roster_id=roster.id
            )
            .only("id")
            .first()
        )

        if existing_attendance:
            raise serializers.ValidationError(
                {
                    "clock_in": (
                        "Employee sudah melakukan "
                        "clock-in untuk shift ini."
                    )
                }
            )

        shift = roster.shift_master

        shift_start = make_shift_datetime(
            roster.date,
            shift.start_time,
        )

        late_limit = (
            shift_start
            + timedelta(
                minutes=(
                    shift.tolerance_minutes
                )
            )
        )

        if now > late_limit:
            attendance_status = "late"
        else:
            attendance_status = "present"

        attendance = (
            AttendanceLog.objects.create(
                employee_id=employee.id,
                roster_id=roster.id,
                clock_in_time=now,
                clock_in_lat=lat,
                clock_in_lng=lng,
                clock_in_photo_url=photo_url,
                status=attendance_status,
            )
        )

    return attendance


# =========================================================
# ATT-01
# CLOCK OUT
# =========================================================

def clock_out_employee(user):
    employee = get_employee_from_user(
        user
    )

    now = timezone.now()

    with transaction.atomic():

        attendance = (
            AttendanceLog.objects
            .select_for_update()
            .select_related(
                "roster__shift_master"
            )
            .filter(
                employee_id=employee.id,
                clock_in_time__isnull=False,
                clock_out_time__isnull=True,
            )
            .order_by(
                "-clock_in_time"
            )
            .first()
        )

        if attendance is None:
            raise serializers.ValidationError(
                {
                    "clock_out": (
                        "Tidak ada clock-in aktif "
                        "yang dapat di-clock-out."
                    )
                }
            )

        if attendance.roster is None:
            raise serializers.ValidationError(
                {
                    "roster": (
                        "Data roster untuk "
                        "attendance ini tidak tersedia."
                    )
                }
            )

        roster = attendance.roster

        shift = roster.shift_master

        shift_end = make_shift_datetime(
            roster.date,
            shift.end_time,
        )

        # Shift lintas hari.
        # Contoh 22:00 - 06:00
        if shift.end_time <= shift.start_time:
            shift_end += timedelta(
                days=1
            )

        attendance.clock_out_time = now

        if now < shift_end:
            attendance.status = (
                "early_leave"
            )

        attendance.save(
            update_fields=[
                "clock_out_time",
                "status",
            ]
        )

    return attendance


# =========================================================
# ATT-02
# SUMMARY / REKAP ATTENDANCE
# =========================================================

def get_attendance_summary(
    month,
    year,
    employee_id=None,
    department_id=None,
    division_id=None,
):
    first_date = date(
        year,
        month,
        1,
    )

    last_date = date(
        year,
        month,
        monthrange(
            year,
            month,
        )[1],
    )

    today = timezone.localdate()

    # Jangan menganggap roster masa depan
    # sebagai mangkir.
    if first_date > today:
        effective_end_date = None
    else:
        effective_end_date = min(
            last_date,
            today,
        )

    if effective_end_date is None:
        return {
            "period": {
                "month": month,
                "year": year,
            },
            "filters": {
                "employee_id": employee_id,
                "department_id": department_id,
                "division_id": division_id,
            },
            "summary": {
                "employee_count": 0,
                "scheduled_days": 0,
                "attended_days": 0,
                "late_count": 0,
                "early_leave_count": 0,
                "absent_count": 0,
                "total_work_hours": 0,
            },
            "employees": [],
        }

    roster_queryset = (
        ShiftRoster.objects
        .filter(
            date__gte=first_date,
            date__lte=effective_end_date,
        )
    )

    if employee_id:
        roster_queryset = (
            roster_queryset.filter(
                employee_id=employee_id
            )
        )

    if department_id:
        roster_queryset = (
            roster_queryset.filter(
                employee__job_title__department_id=(
                    department_id
                )
            )
        )

    if division_id:
        roster_queryset = (
            roster_queryset.filter(
                employee__job_title__department__division_id=(
                    division_id
                )
            )
        )

    # Satu query roster + data Employee,
    # Department, Division, ShiftMaster.
    roster_rows = list(
        roster_queryset.values(
            "id",
            "employee_id",
            "employee__employee_code",
            "employee__full_name",

            "employee__job_title__department_id",
            "employee__job_title__department__name",

            (
                "employee__job_title__"
                "department__division_id"
            ),
            (
                "employee__job_title__"
                "department__division__name"
            ),

            "date",
            "shift_master__start_time",
            "shift_master__end_time",
            "shift_master__tolerance_minutes",
        )
    )

    roster_ids = [
        roster["id"]
        for roster in roster_rows
    ]

    attendance_rows = []

    if roster_ids:
        attendance_rows = list(
            AttendanceLog.objects
            .filter(
                roster_id__in=roster_ids
            )
            .values(
                "id",
                "roster_id",
                "employee_id",
                "clock_in_time",
                "clock_out_time",
                "status",
            )
            .order_by(
                "roster_id",
                "clock_in_time",
            )
        )

    # ATT-01 seharusnya hanya membuat satu
    # AttendanceLog per roster.
    #
    # setdefault() memastikan jika ada data
    # duplikat lama, record pertama saja
    # yang digunakan dalam rekap.
    attendance_by_roster = {}

    for attendance in attendance_rows:
        attendance_by_roster.setdefault(
            attendance["roster_id"],
            attendance,
        )

    employee_summary = {}

    for roster in roster_rows:
        employee_key = roster[
            "employee_id"
        ]

        if employee_key not in employee_summary:
            employee_summary[
                employee_key
            ] = {
                "employee_id": employee_key,

                "employee_code": roster[
                    "employee__employee_code"
                ],

                "full_name": roster[
                    "employee__full_name"
                ],

                "department": {
                    "id": roster[
                        (
                            "employee__job_title__"
                            "department_id"
                        )
                    ],
                    "name": roster[
                        (
                            "employee__job_title__"
                            "department__name"
                        )
                    ],
                },

                "division": {
                    "id": roster[
                        (
                            "employee__job_title__"
                            "department__division_id"
                        )
                    ],
                    "name": roster[
                        (
                            "employee__job_title__"
                            "department__division__name"
                        )
                    ],
                },

                "scheduled_days": 0,
                "attended_days": 0,
                "late_count": 0,
                "early_leave_count": 0,
                "absent_count": 0,

                "_work_seconds": 0,
            }

        employee_data = employee_summary[
            employee_key
        ]

        employee_data[
            "scheduled_days"
        ] += 1

        attendance = (
            attendance_by_roster.get(
                roster["id"]
            )
        )

        # Tidak clock-in pada roster
        # yang sudah lewat = mangkir.
        if (
            attendance is None
            or attendance[
                "clock_in_time"
            ] is None
        ):
            employee_data[
                "absent_count"
            ] += 1

            continue

        employee_data[
            "attended_days"
        ] += 1

        clock_in = normalize_datetime(
            attendance[
                "clock_in_time"
            ]
        )

        clock_out = normalize_datetime(
            attendance[
                "clock_out_time"
            ]
        )

        shift_start = make_shift_datetime(
            roster["date"],
            roster[
                "shift_master__start_time"
            ],
        )

        shift_end = make_shift_datetime(
            roster["date"],
            roster[
                "shift_master__end_time"
            ],
        )

        if (
            roster[
                "shift_master__end_time"
            ]
            <=
            roster[
                "shift_master__start_time"
            ]
        ):
            shift_end += timedelta(
                days=1
            )

        late_limit = (
            shift_start
            + timedelta(
                minutes=roster[
                    (
                        "shift_master__"
                        "tolerance_minutes"
                    )
                ]
            )
        )

        # Hitung late langsung dari jam,
        # bukan hanya kolom status.
        if clock_in > late_limit:
            employee_data[
                "late_count"
            ] += 1

        # Hitung early leave langsung
        # dari clock_out vs end shift.
        if (
            clock_out is not None
            and clock_out < shift_end
        ):
            employee_data[
                "early_leave_count"
            ] += 1

        if (
            clock_in is not None
            and clock_out is not None
            and clock_out >= clock_in
        ):
            worked_seconds = (
                clock_out - clock_in
            ).total_seconds()

            employee_data[
                "_work_seconds"
            ] += worked_seconds

    employees = []

    for employee_data in (
        employee_summary.values()
    ):
        work_seconds = employee_data.pop(
            "_work_seconds"
        )

        employee_data[
            "total_work_hours"
        ] = round(
            work_seconds / 3600,
            2,
        )

        employees.append(
            employee_data
        )

    employees.sort(
        key=lambda item: (
            item["employee_id"]
        )
    )

    summary = {
        "employee_count": len(
            employees
        ),

        "scheduled_days": sum(
            item["scheduled_days"]
            for item in employees
        ),

        "attended_days": sum(
            item["attended_days"]
            for item in employees
        ),

        "late_count": sum(
            item["late_count"]
            for item in employees
        ),

        "early_leave_count": sum(
            item["early_leave_count"]
            for item in employees
        ),

        "absent_count": sum(
            item["absent_count"]
            for item in employees
        ),

        "total_work_hours": round(
            sum(
                item["total_work_hours"]
                for item in employees
            ),
            2,
        ),
    }

    return {
        "period": {
            "month": month,
            "year": year,
            "start_date": (
                first_date.isoformat()
            ),
            "end_date": (
                effective_end_date
                .isoformat()
            ),
        },

        "filters": {
            "employee_id": employee_id,
            "department_id": department_id,
            "division_id": division_id,
        },

        "summary": summary,

        "employees": employees,
    }
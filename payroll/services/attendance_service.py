from attendance.models import AttendanceLog


def get_attendance_days(employee_id, month, year):
    attendance_days = (
        AttendanceLog.objects
        .filter(
            employee_id=employee_id,
            clock_in_time__isnull=False,
            clock_in_time__month=month,
            clock_in_time__year=year,
        )
        .values("clock_in_time__date")
        .distinct()
        .count()
    )

    return attendance_days
from django.urls import path

from .views import (
    AttendanceSummaryView,
    ClockInView,
    ClockOutView,
)


urlpatterns = [
    path(
        "clock-in/",
        ClockInView.as_view(),
        name="attendance-clock-in",
    ),

    path(
        "clock-out/",
        ClockOutView.as_view(),
        name="attendance-clock-out",
    ),

    path(
        "summary/",
        AttendanceSummaryView.as_view(),
        name="attendance-summary",
    ),
]
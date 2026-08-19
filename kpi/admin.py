from django.contrib import admin

from .models import (
    KpiAppraisal,
    KpiGoal,
)


@admin.register(KpiGoal)
class KpiGoalAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "employee",
        "title",
        "period_type",
        "year",
        "quarter",
        "weight",
        "target_value",
        "status",
        "approved_by",
    ]

    list_filter = [
        "period_type",
        "year",
        "quarter",
        "status",
    ]

    search_fields = [
        "employee__employee_code",
        "employee__full_name",
        "title",
    ]

@admin.register(KpiAppraisal)
class KpiAppraisalAdmin(
    admin.ModelAdmin
):

    list_display = [
        "id",
        "employee",
        "reviewer",
        "appraisal_type",
        "period_type",
        "year",
        "quarter",
        "score",
        "submitted_at",
    ]

    list_filter = [
        "appraisal_type",
        "period_type",
        "year",
        "quarter",
    ]

    search_fields = [
        "employee__employee_code",
        "employee__full_name",
        "reviewer__employee_code",
        "reviewer__full_name",
    ]
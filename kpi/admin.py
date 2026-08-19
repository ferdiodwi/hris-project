from django.contrib import admin

from .models import KpiGoal


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
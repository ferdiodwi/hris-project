from django.contrib import admin

from .models import (
    Branch,
    Directorate,
    Division,
    Department,
    JobTitle,
)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "address",
        "created_at",
    )
    search_fields = (
        "name",
        "address",
    )
    ordering = ("name",)


@admin.register(Directorate)
class DirectorateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "branch",
    )
    search_fields = (
        "name",
        "branch__name",
    )
    list_filter = (
        "branch",
    )
    ordering = ("name",)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "directorate",
    )
    search_fields = (
        "name",
        "directorate__name",
        "directorate__branch__name",
    )
    list_filter = (
        "directorate",
    )
    ordering = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "division",
    )
    search_fields = (
        "name",
        "division__name",
        "division__directorate__name",
    )
    list_filter = (
        "division",
    )
    ordering = ("name",)


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "job_level",
        "department",
    )
    search_fields = (
        "name",
        "job_level",
        "department__name",
    )
    list_filter = (
        "job_level",
        "department",
    )
    ordering = ("name",)
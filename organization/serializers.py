from rest_framework import serializers

from .models import (
    Branch,
    Directorate,
    Division,
    Department,
    JobTitle,
)


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = (
            "id",
            "name",
            "address",
            "created_at",
        )
        read_only_fields = (
            "id",
            "created_at",
        )


class DirectorateSerializer(serializers.ModelSerializer):
    branch_id = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source="branch",
        write_only=True,
    )

    branch = BranchSerializer(
        read_only=True,
    )

    class Meta:
        model = Directorate
        fields = (
            "id",
            "name",
            "branch_id",
            "branch",
        )
        read_only_fields = (
            "id",
        )


class DivisionSerializer(serializers.ModelSerializer):
    directorate_id = serializers.PrimaryKeyRelatedField(
        queryset=Directorate.objects.all(),
        source="directorate",
        write_only=True,
    )

    directorate = DirectorateSerializer(
        read_only=True,
    )

    class Meta:
        model = Division
        fields = (
            "id",
            "name",
            "directorate_id",
            "directorate",
        )
        read_only_fields = (
            "id",
        )


class DepartmentSerializer(serializers.ModelSerializer):
    division_id = serializers.PrimaryKeyRelatedField(
        queryset=Division.objects.all(),
        source="division",
        write_only=True,
    )

    division = DivisionSerializer(
        read_only=True,
    )

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "division_id",
            "division",
        )
        read_only_fields = (
            "id",
        )


class JobTitleSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="department",
        write_only=True,
    )

    department = DepartmentSerializer(
        read_only=True,
    )

    class Meta:
        model = JobTitle
        fields = (
            "id",
            "name",
            "job_level",
            "department_id",
            "department",
        )
        read_only_fields = (
            "id",
        )
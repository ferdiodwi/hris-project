from rest_framework import serializers

from .models import (
    KpiAppraisal,
    KpiGoal,
)


class KpiGoalSerializer(serializers.ModelSerializer):

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    approved_by_name = serializers.CharField(
        source="approved_by.full_name",
        read_only=True,
    )

    class Meta:
        model = KpiGoal

        fields = [
            "id",
            "employee",
            "employee_code",
            "employee_name",
            "title",
            "description",
            "period_type",
            "year",
            "quarter",
            "weight",
            "target_value",
            "unit",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "employee",
            "target_value",
            "status",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        if self.instance:
            period_type = attrs.get(
                "period_type",
                self.instance.period_type,
            )

            quarter = attrs.get(
                "quarter",
                self.instance.quarter,
            )

        else:
            period_type = attrs.get(
                "period_type"
            )

            quarter = attrs.get(
                "quarter"
            )

        if (
            period_type
            == KpiGoal.PeriodType.QUARTERLY
        ):
            if quarter is None:
                raise serializers.ValidationError(
                    {
                        "quarter": (
                            "Quarter wajib diisi "
                            "untuk goal QUARTERLY."
                        )
                    }
                )

            if quarter not in [
                1,
                2,
                3,
                4,
            ]:
                raise serializers.ValidationError(
                    {
                        "quarter": (
                            "Quarter hanya boleh "
                            "1, 2, 3, atau 4."
                        )
                    }
                )

        if (
            period_type
            == KpiGoal.PeriodType.YEARLY
        ):
            attrs["quarter"] = None

        return attrs


class KpiGoalSetTargetSerializer(
    serializers.Serializer
):

    target_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
    )

class KpiAppraisalSerializer(
    serializers.ModelSerializer
):

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
    )

    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    reviewer_code = serializers.CharField(
        source="reviewer.employee_code",
        read_only=True,
    )

    reviewer_name = serializers.CharField(
        source="reviewer.full_name",
        read_only=True,
    )

    class Meta:
        model = KpiAppraisal

        fields = [
            "id",
            "employee",
            "employee_code",
            "employee_name",
            "reviewer",
            "reviewer_code",
            "reviewer_name",
            "appraisal_type",
            "period_type",
            "year",
            "quarter",
            "score",
            "comment",
            "submitted_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "reviewer",
            "submitted_at",
            "updated_at",
        ]

    def validate(self, attrs):

        period_type = attrs.get(
            "period_type"
        )

        quarter = attrs.get(
            "quarter"
        )

        if (
            period_type
            == KpiGoal.PeriodType.QUARTERLY
        ):
            if quarter is None:
                raise serializers.ValidationError(
                    {
                        "quarter": (
                            "Quarter wajib diisi "
                            "untuk appraisal "
                            "QUARTERLY."
                        )
                    }
                )

        if (
            period_type
            == KpiGoal.PeriodType.YEARLY
        ):
            attrs["quarter"] = None

        return attrs

class KpiFinalScoreQuerySerializer(
    serializers.Serializer
):

    employee_id = serializers.IntegerField(
        min_value=1,
    )

    period_type = serializers.ChoiceField(
        choices=KpiGoal.PeriodType.choices,
    )

    year = serializers.IntegerField(
        min_value=2000,
        max_value=2100,
    )

    quarter = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=4,
    )

    manager_weight = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        default=1,
        min_value=0,
    )

    peer_weight = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        default=1,
        min_value=0,
    )

    self_weight = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        default=1,
        min_value=0,
    )

    def validate(self, attrs):

        period_type = attrs[
            "period_type"
        ]

        if (
            period_type
            == KpiGoal.PeriodType.QUARTERLY
            and attrs.get("quarter") is None
        ):
            raise serializers.ValidationError(
                {
                    "quarter": (
                        "Quarter wajib diisi "
                        "untuk periode QUARTERLY."
                    )
                }
            )

        if (
            period_type
            == KpiGoal.PeriodType.YEARLY
        ):
            attrs["quarter"] = None

        total_weight = (
            attrs["manager_weight"]
            + attrs["peer_weight"]
            + attrs["self_weight"]
        )

        if total_weight <= 0:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Total weight harus "
                        "lebih besar dari 0."
                    )
                }
            )

        return attrs
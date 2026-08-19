from rest_framework import serializers

from .models import KpiGoal


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
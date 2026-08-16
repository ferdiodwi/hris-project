from rest_framework import serializers

from .models import SalaryComponent


class SalaryComponentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalaryComponent
        fields = [
            "id",
            "employee_id",
            "component_type",
            "name",
            "calculation_method",
            "amount",
            "rate_per_day",
            "is_active",
        ]

        read_only_fields = ["id"]

    def validate(self, attrs):
        calculation_method = attrs.get(
            "calculation_method",
            getattr(
                self.instance,
                "calculation_method",
                SalaryComponent.CalculationMethod.FIXED
            )
        )

        rate_per_day = attrs.get(
            "rate_per_day",
            getattr(
                self.instance,
                "rate_per_day",
                None
            )
        )

        amount = attrs.get(
            "amount",
            getattr(
                self.instance,
                "amount",
                0
            )
        )

        if amount is not None and amount < 0:
            raise serializers.ValidationError({
                "amount": "Amount tidak boleh negatif."
            })

        if (
            calculation_method
            == SalaryComponent.CalculationMethod.ATTENDANCE
        ):
            if rate_per_day is None or rate_per_day <= 0:
                raise serializers.ValidationError({
                    "rate_per_day":
                        "Rate per day wajib lebih dari 0 untuk komponen attendance."
                })

        return attrs
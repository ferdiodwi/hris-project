from rest_framework import serializers

from .models import SalaryComponent
from .models import (
    PayrollProfile,
    PayrollRun,
    Payslip,
)


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


class MealAllowanceCalculationSerializer(
    serializers.Serializer
):
    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
        required=True,
    )

    year = serializers.IntegerField(
        min_value=2000,
        required=True,
    )

class PayrollProfileSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PayrollProfile

        fields = [
            "id",
            "employee",
            "ptkp_status",
            "bpjs_wage",
            "jkk_risk",
            "bpjs_ketenagakerjaan_active",
            "bpjs_kesehatan_active",
        ]


class PayrollRunPay02Serializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PayrollRun

        fields = [
            "id",
            "period_month",
            "period_year",
            "status",
            "processed_at",
        ]

        read_only_fields = [
            "status",
            "processed_at",
        ]

    def validate_period_month(
        self,
        value,
    ):
        if value < 1 or value > 12:
            raise serializers.ValidationError(
                "period_month harus 1 sampai 12."
            )

        return value


class PayslipPay02Serializer(
    serializers.ModelSerializer
):
    employee_name = serializers.CharField(
        source="employee.full_name",
        read_only=True,
    )

    class Meta:
        model = Payslip

        fields = [
            "id",
            "payroll_run",
            "employee",
            "employee_name",
            "gross_salary",
            "pph21_amount",
            "bpjs_amount",
            "total_deduction",
            "net_salary",
            "calculation_detail",
        ]

        read_only_fields = [
            "id",
            "payroll_run",
            "employee",
            "employee_name",
            "gross_salary",
            "pph21_amount",
            "bpjs_amount",
            "total_deduction",
            "net_salary",
            "calculation_detail",
        ]
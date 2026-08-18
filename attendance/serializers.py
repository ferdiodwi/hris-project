from rest_framework import serializers

from .models import AttendanceLog


class ClockInSerializer(serializers.Serializer):
    clock_in_lat = serializers.DecimalField(
        max_digits=10,
        decimal_places=6,
        required=True,
    )

    clock_in_lng = serializers.DecimalField(
        max_digits=10,
        decimal_places=6,
        required=True,
    )

    clock_in_photo_url = serializers.URLField(
        max_length=255,
        required=True,
        allow_blank=False,
    )

    def validate_clock_in_lat(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError(
                "Latitude harus berada antara -90 dan 90."
            )

        return value

    def validate_clock_in_lng(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError(
                "Longitude harus berada antara -180 dan 180."
            )

        return value


class AttendanceLogSerializer(
    serializers.ModelSerializer
):
    employee_id = serializers.IntegerField(
        read_only=True
    )

    roster_id = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = AttendanceLog

        fields = [
            "id",
            "employee_id",
            "roster_id",
            "clock_in_time",
            "clock_out_time",
            "clock_in_lat",
            "clock_in_lng",
            "clock_in_photo_url",
            "status",
        ]

        read_only_fields = fields


class AttendanceSummaryQuerySerializer(
    serializers.Serializer
):
    employee_id = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    month = serializers.IntegerField(
        min_value=1,
        max_value=12,
        required=True,
    )

    year = serializers.IntegerField(
        min_value=1,
        required=True,
    )

    department_id = serializers.IntegerField(
        min_value=1,
        required=False,
    )

    division_id = serializers.IntegerField(
        min_value=1,
        required=False,
    )
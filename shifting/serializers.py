from rest_framework import serializers

from .models import ShiftMaster


class ShiftMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftMaster
        fields = [
            "id",
            "name",
            "start_time",
            "end_time",
            "tolerance_minutes",
        ]
        read_only_fields = ["id"]

    def validate_tolerance_minutes(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Toleransi keterlambatan tidak boleh negatif."
            )

        return value
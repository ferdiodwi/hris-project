from rest_framework import serializers

from .models import (
    ShiftMaster,
    ShiftRoster,
)


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

        read_only_fields = [
            "id",
        ]

    def validate_tolerance_minutes(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Toleransi keterlambatan tidak boleh negatif."
            )

        return value


class ShiftRosterSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField()

    shift_master_id = serializers.IntegerField()

    class Meta:
        model = ShiftRoster

        fields = [
            "id",
            "employee_id",
            "shift_master_id",
            "date",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_employee_id(self, value):
        Employee = (
            ShiftRoster._meta
            .get_field("employee")
            .remote_field
            .model
        )

        if not Employee.objects.filter(
            pk=value
        ).exists():
            raise serializers.ValidationError(
                "Employee tidak ditemukan."
            )

        return value

    def validate_shift_master_id(self, value):
        if not ShiftMaster.objects.filter(
            pk=value
        ).exists():
            raise serializers.ValidationError(
                "Shift master tidak ditemukan."
            )

        return value

    def validate(self, attrs):
        employee_id = attrs.get(
            "employee_id",
            getattr(
                self.instance,
                "employee_id",
                None,
            ),
        )

        date = attrs.get(
            "date",
            getattr(
                self.instance,
                "date",
                None,
            ),
        )

        if employee_id is None or date is None:
            return attrs

        queryset = ShiftRoster.objects.filter(
            employee_id=employee_id,
            date=date,
        )

        if self.instance is not None:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        (
                            "Employee sudah memiliki "
                            "roster pada tanggal tersebut."
                        )
                    ]
                }
            )

        return attrs


class BulkAssignRosterSerializer(
    serializers.Serializer
):
    shift_master_id = serializers.IntegerField(
        min_value=1,
    )

    employee_ids = serializers.ListField(
        child=serializers.IntegerField(
            min_value=1,
        ),
        allow_empty=False,
    )

    dates = serializers.ListField(
        child=serializers.DateField(),
        allow_empty=False,
    )

    def validate_shift_master_id(self, value):
        if not ShiftMaster.objects.filter(
            pk=value
        ).exists():
            raise serializers.ValidationError(
                "Shift master tidak ditemukan."
            )

        return value

    def validate_employee_ids(self, value):
        # Menghapus ID employee duplikat
        # sambil mempertahankan urutan.
        employee_ids = list(
            dict.fromkeys(value)
        )

        Employee = (
            ShiftRoster._meta
            .get_field("employee")
            .remote_field
            .model
        )

        existing_ids = set(
            Employee.objects.filter(
                id__in=employee_ids
            ).values_list(
                "id",
                flat=True,
            )
        )

        missing_ids = [
            employee_id
            for employee_id in employee_ids
            if employee_id not in existing_ids
        ]

        if missing_ids:
            raise serializers.ValidationError(
                {
                    "message": (
                        "Beberapa employee "
                        "tidak ditemukan."
                    ),
                    "employee_ids": missing_ids,
                }
            )

        return employee_ids

    def validate_dates(self, value):
        # Menghapus tanggal duplikat.
        return list(
            dict.fromkeys(value)
        )

    def validate(self, attrs):
        employee_ids = attrs[
            "employee_ids"
        ]

        dates = attrs[
            "dates"
        ]

        conflicts = list(
            ShiftRoster.objects.filter(
                employee_id__in=employee_ids,
                date__in=dates,
            ).values(
                "employee_id",
                "date",
            )
        )

        if conflicts:
            raise serializers.ValidationError(
                {
                    "message": (
                        "Sebagian employee sudah "
                        "memiliki roster pada "
                        "tanggal yang dipilih."
                    ),
                    "conflicts": conflicts,
                }
            )

        return attrs

    def create(self, validated_data):
        shift_master_id = validated_data[
            "shift_master_id"
        ]

        employee_ids = validated_data[
            "employee_ids"
        ]

        dates = validated_data[
            "dates"
        ]

        rosters = [
            ShiftRoster(
                employee_id=employee_id,
                shift_master_id=shift_master_id,
                date=date,
            )
            for employee_id in employee_ids
            for date in dates
        ]

        ShiftRoster.objects.bulk_create(
            rosters
        )

        return ShiftRoster.objects.filter(
            employee_id__in=employee_ids,
            shift_master_id=shift_master_id,
            date__in=dates,
        ).order_by(
            "date",
            "employee_id",
        )
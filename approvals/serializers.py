from rest_framework import serializers

from .models import (
    ApprovalRequest,
    ApprovalStep,
)


class ApprovalRequestSerializer(
    serializers.ModelSerializer
):
    employee_id = serializers.IntegerField(
        read_only=True
    )

    status = serializers.CharField(
        read_only=True
    )

    created_at = serializers.DateTimeField(
        read_only=True
    )

    class Meta:
        model = ApprovalRequest

        fields = [
            "id",
            "employee_id",
            "request_type",
            "start_date",
            "end_date",
            "attachment_url",
            "amount",
            "reason",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "employee_id",
            "status",
            "created_at",
        ]

        extra_kwargs = {
            "start_date": {
                "required": False,
                "allow_null": True,
            },

            "end_date": {
                "required": False,
                "allow_null": True,
            },

            "attachment_url": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },

            "amount": {
                "required": False,
                "allow_null": True,
            },

            "reason": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
        }

    def validate_request_type(
        self,
        value,
    ):
        allowed_types = [
            "cuti_tahunan",
            "izin",
            "sakit",
            "reimbursement",
            "lembur",
        ]

        if value not in allowed_types:
            raise serializers.ValidationError(
                (
                    "request_type harus salah satu dari: "
                    "cuti_tahunan, izin, sakit, "
                    "reimbursement, lembur."
                )
            )

        return value

    def validate(
        self,
        attrs,
    ):
        request_type = attrs.get(
            "request_type"
        )

        attachment_url = attrs.get(
            "attachment_url"
        )

        amount = attrs.get(
            "amount"
        )

        if (
            request_type == "sakit"
            and not attachment_url
        ):
            raise serializers.ValidationError(
                {
                    "attachment_url": [
                        (
                            "Surat dokter wajib "
                            "untuk pengajuan sakit."
                        )
                    ]
                }
            )

        if (
            request_type
            in [
                "reimbursement",
                "lembur",
            ]
            and amount is None
        ):
            raise serializers.ValidationError(
                {
                    "amount": [
                        (
                            "Amount wajib untuk "
                            f"pengajuan {request_type}."
                        )
                    ]
                }
            )

        return attrs


class ApprovalStepSerializer(
    serializers.ModelSerializer
):
    request_id = serializers.IntegerField(
        read_only=True
    )

    approver_id = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = ApprovalStep

        fields = [
            "id",
            "request_id",
            "approver_id",
            "level",
            "decision",
            "decided_at",
            "note",
        ]

        read_only_fields = fields


class ApprovalDecisionSerializer(
    serializers.Serializer
):
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
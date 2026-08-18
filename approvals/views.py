from django.db import transaction

from rest_framework import (
    generics,
    status,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from accounts.models import Employee

from .models import ApprovalRequest

from .serializers import (
    ApprovalDecisionSerializer,
    ApprovalRequestSerializer,
    ApprovalStepSerializer,
)

from .services import (
    create_initial_approval_step,
    process_approval_decision,
)


class ApprovalRequestCreateView(
    generics.CreateAPIView
):
    queryset = ApprovalRequest.objects.all()

    serializer_class = (
        ApprovalRequestSerializer
    )

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def perform_create(
        self,
        serializer,
    ):
        employee = (
            Employee.objects
            .select_related(
                "reports_to"
            )
            .get(
                user_id=self.request.user.id
            )
        )

        with transaction.atomic():

            approval_request = (
                serializer.save(
                    employee=employee,
                    status="pending",
                )
            )

            create_initial_approval_step(
                approval_request
            )


class ApprovalRequestApproveView(
    APIView
):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
        pk,
    ):
        serializer = (
            ApprovalDecisionSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = (
            process_approval_decision(
                user=request.user,
                request_id=pk,
                decision="approved",
                note=(
                    serializer
                    .validated_data
                    .get("note")
                ),
            )
        )

        response = {
            "message": (
                "Approval berhasil diproses."
            ),

            "request": (
                ApprovalRequestSerializer(
                    result["request"]
                ).data
            ),

            "processed_step": (
                ApprovalStepSerializer(
                    result[
                        "processed_step"
                    ]
                ).data
            ),

            "next_step": None,
        }

        if result["next_step"]:
            response["next_step"] = (
                ApprovalStepSerializer(
                    result["next_step"]
                ).data
            )

        return Response(
            response,
            status=status.HTTP_200_OK,
        )


class ApprovalRequestRejectView(
    APIView
):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
        pk,
    ):
        serializer = (
            ApprovalDecisionSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = (
            process_approval_decision(
                user=request.user,
                request_id=pk,
                decision="rejected",
                note=(
                    serializer
                    .validated_data
                    .get("note")
                ),
            )
        )

        return Response(
            {
                "message": (
                    "Approval request ditolak."
                ),

                "request": (
                    ApprovalRequestSerializer(
                        result["request"]
                    ).data
                ),

                "processed_step": (
                    ApprovalStepSerializer(
                        result[
                            "processed_step"
                        ]
                    ).data
                ),
            },

            status=status.HTTP_200_OK,
        )
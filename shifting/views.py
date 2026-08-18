from django.db import (
    IntegrityError,
    transaction,
)

from rest_framework import (
    status,
    viewsets,
)

from rest_framework.decorators import action

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response

from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
)

from .models import (
    ShiftMaster,
    ShiftRoster,
)

from .serializers import (
    BulkAssignRosterSerializer,
    ShiftMasterSerializer,
    ShiftRosterSerializer,
)


class ShiftMasterViewSet(
    viewsets.ModelViewSet
):
    queryset = (
        ShiftMaster.objects
        .all()
        .order_by("id")
    )

    serializer_class = (
        ShiftMasterSerializer
    )

    # JWT Authentication
    authentication_classes = [
        JWTAuthentication,
    ]

    # Wajib sudah login / punya JWT valid
    permission_classes = [
        IsAuthenticated,
    ]


class ShiftRosterViewSet(
    viewsets.ModelViewSet
):
    serializer_class = (
        ShiftRosterSerializer
    )

    # JWT Authentication
    authentication_classes = [
        JWTAuthentication,
    ]

    # Wajib sudah login / punya JWT valid
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = (
            ShiftRoster.objects
            .select_related(
                "employee",
                "shift_master",
            )
            .order_by(
                "date",
                "employee_id",
            )
        )

        employee_id = (
            self.request
            .query_params
            .get("employee_id")
        )

        start_date = (
            self.request
            .query_params
            .get("start_date")
        )

        end_date = (
            self.request
            .query_params
            .get("end_date")
        )

        shift_master_id = (
            self.request
            .query_params
            .get("shift_master_id")
        )

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        if shift_master_id:
            queryset = queryset.filter(
                shift_master_id=shift_master_id
            )

        if start_date:
            queryset = queryset.filter(
                date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                date__lte=end_date
            )

        return queryset

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-assign",
    )
    def bulk_assign(
        self,
        request,
    ):
        serializer = (
            BulkAssignRosterSerializer(
                data=request.data
            )
        )

        try:
            with transaction.atomic():
                serializer.is_valid(
                    raise_exception=True
                )

                created_rosters = (
                    serializer.save()
                )

                results = (
                    ShiftRosterSerializer(
                        created_rosters,
                        many=True,
                    ).data
                )

        except IntegrityError:
            return Response(
                {
                    "message": (
                        "Gagal membuat roster "
                        "karena terdapat data "
                        "yang bentrok."
                    )
                },
                status=(
                    status.HTTP_409_CONFLICT
                ),
            )

        return Response(
            {
                "message": (
                    "Roster berhasil dibuat."
                ),
                "created_count": len(
                    results
                ),
                "results": results,
            },
            status=(
                status.HTTP_201_CREATED
            ),
        )
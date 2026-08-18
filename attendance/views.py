from rest_framework import (
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

from .serializers import (
    AttendanceLogSerializer,
    AttendanceSummaryQuerySerializer,
    ClockInSerializer,
)

from .services import (
    clock_in_employee,
    clock_out_employee,
    get_attendance_summary,
)


# =========================================================
# ATT-01
# CLOCK IN
# =========================================================

class ClockInView(APIView):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = ClockInSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        attendance = clock_in_employee(
            user=request.user,

            lat=(
                serializer.validated_data[
                    "clock_in_lat"
                ]
            ),

            lng=(
                serializer.validated_data[
                    "clock_in_lng"
                ]
            ),

            photo_url=(
                serializer.validated_data[
                    "clock_in_photo_url"
                ]
            ),
        )

        response_data = (
            AttendanceLogSerializer(
                attendance
            ).data
        )

        return Response(
            {
                "message": (
                    "Clock-in berhasil."
                ),

                "data": response_data,
            },

            status=(
                status.HTTP_201_CREATED
            ),
        )


# =========================================================
# ATT-01
# CLOCK OUT
# =========================================================

class ClockOutView(APIView):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        attendance = clock_out_employee(
            request.user
        )

        response_data = (
            AttendanceLogSerializer(
                attendance
            ).data
        )

        return Response(
            {
                "message": (
                    "Clock-out berhasil."
                ),

                "data": response_data,
            },

            status=(
                status.HTTP_200_OK
            ),
        )


# =========================================================
# ATT-02
# SUMMARY
# =========================================================

class AttendanceSummaryView(APIView):
    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        serializer = (
            AttendanceSummaryQuerySerializer(
                data=request.query_params
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        summary = get_attendance_summary(
            employee_id=data.get(
                "employee_id"
            ),

            month=data["month"],

            year=data["year"],

            department_id=data.get(
                "department_id"
            ),

            division_id=data.get(
                "division_id"
            ),
        )

        return Response(
            summary,
            status=status.HTTP_200_OK,
        )
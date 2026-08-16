from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from uam.permissions import HasRBACPermission

from .models import (
    Branch,
    Directorate,
    Division,
    Department,
    JobTitle,
)

from .serializers import (
    BranchSerializer,
    DirectorateSerializer,
    DivisionSerializer,
    DepartmentSerializer,
    JobTitleSerializer,
)


class OrganizationBaseViewSet(ModelViewSet):
    """
    Base ViewSet untuk seluruh endpoint Organization.

    Authentication:
    - JWT

    Authorization:
    - User harus authenticated
    - User harus memiliki RBAC permission untuk module
      'Organization Management'
    """

    authentication_classes = [JWTAuthentication]

    permission_classes = [
        IsAuthenticated,
        HasRBACPermission,
    ]

    rbac_module = "Organization Management"


class BranchViewSet(OrganizationBaseViewSet):
    queryset = Branch.objects.all().order_by("id")
    serializer_class = BranchSerializer


class DirectorateViewSet(OrganizationBaseViewSet):
    queryset = (
        Directorate.objects
        .select_related("branch")
        .all()
        .order_by("id")
    )

    serializer_class = DirectorateSerializer


class DivisionViewSet(OrganizationBaseViewSet):
    queryset = (
        Division.objects
        .select_related(
            "directorate",
            "directorate__branch",
        )
        .all()
        .order_by("id")
    )

    serializer_class = DivisionSerializer


class DepartmentViewSet(OrganizationBaseViewSet):
    queryset = (
        Department.objects
        .select_related(
            "division",
            "division__directorate",
            "division__directorate__branch",
        )
        .all()
        .order_by("id")
    )

    serializer_class = DepartmentSerializer


class JobTitleViewSet(OrganizationBaseViewSet):
    queryset = (
        JobTitle.objects
        .select_related(
            "department",
            "department__division",
            "department__division__directorate",
            "department__division__directorate__branch",
        )
        .all()
        .order_by("id")
    )

    serializer_class = JobTitleSerializer
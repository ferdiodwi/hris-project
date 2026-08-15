from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import UserRole, RolePermission
from .serializers import UserRoleSerializer, RolePermissionSerializer
from .permissions import HasRBACPermission

class AssignRoleView(generics.CreateAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, HasRBACPermission]
    rbac_module = 'User Access Management'

class AssignPermissionView(generics.CreateAPIView):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, HasRBACPermission]
    rbac_module = 'User Access Management'

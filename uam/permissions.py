from rest_framework.permissions import BasePermission
from uam.models import RolePermission

class HasRBACPermission(BasePermission):
    """
    Permission class untuk RBAC.
    View yang menggunakan class ini wajib mendefinisikan atribut `rbac_module`.
    Contoh:
        class GajiView(APIView):
            rbac_module = 'Payroll'
            permission_classes = [IsAuthenticated, HasRBACPermission]
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Bypass untuk Super Admin
        if request.user.user_roles.filter(role__name='Super Admin').exists():
            return True

        module_name = getattr(view, 'rbac_module', None)
        if not module_name:
            return False

        is_read = request.method in ['GET', 'OPTIONS', 'HEAD']
        is_write = request.method in ['POST', 'PUT', 'PATCH']
        is_delete = request.method == 'DELETE'

        user_role_ids = request.user.user_roles.values_list('role_id', flat=True)
        permissions = RolePermission.objects.filter(
            role_id__in=user_role_ids, 
            permission__module=module_name
        ).select_related('permission')

        for rp in permissions:
            if is_read and rp.permission.can_read:
                return True
            if is_write and rp.permission.can_write:
                return True
            if is_delete and rp.permission.can_delete:
                return True

        return False

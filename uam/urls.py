from django.urls import path
from .views import AssignRoleView, AssignPermissionView

urlpatterns = [
    path('assign-role/', AssignRoleView.as_view(), name='assign_role'),
    path('assign-permission/', AssignPermissionView.as_view(), name='assign_permission'),
]

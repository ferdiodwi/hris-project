from django.urls import path

from .views import (
    ApprovalRequestApproveView,
    ApprovalRequestCreateView,
    ApprovalRequestRejectView,
)


urlpatterns = [
    path(
        "",
        ApprovalRequestCreateView.as_view(),
        name="approval-request-create",
    ),

    path(
        "<int:pk>/approve/",
        ApprovalRequestApproveView.as_view(),
        name="approval-request-approve",
    ),

    path(
        "<int:pk>/reject/",
        ApprovalRequestRejectView.as_view(),
        name="approval-request-reject",
    ),
]
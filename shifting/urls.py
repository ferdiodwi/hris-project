from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ShiftMasterViewSet


router = DefaultRouter()

router.register(
    "shift-masters",
    ShiftMasterViewSet,
    basename="shift-master",
)


urlpatterns = [
    path("", include(router.urls)),
]
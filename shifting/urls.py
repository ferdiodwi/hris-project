from django.urls import (
    include,
    path,
)

from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    ShiftMasterViewSet,
    ShiftRosterViewSet,
)


router = DefaultRouter()


router.register(
    "shift-masters",
    ShiftMasterViewSet,
    basename="shift-master",
)


router.register(
    "shift-rosters",
    ShiftRosterViewSet,
    basename="shift-roster",
)


urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]
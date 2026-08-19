from rest_framework.routers import (
    DefaultRouter,
)

from .views import KpiGoalViewSet


router = DefaultRouter()

router.register(
    "goals",
    KpiGoalViewSet,
    basename="kpi-goal",
)


urlpatterns = router.urls
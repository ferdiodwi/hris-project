from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    KpiAppraisalViewSet,
    KpiGoalViewSet,
)


router = DefaultRouter()

router.register(
    "goals",
    KpiGoalViewSet,
    basename="kpi-goal",
)

router.register(
    "appraisals",
    KpiAppraisalViewSet,
    basename="kpi-appraisal",
)


urlpatterns = router.urls
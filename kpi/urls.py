from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    KpiAppraisalViewSet,
    KpiGoalViewSet,
    KpiTaskViewSet,
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


router.register(
    "tasks",
    KpiTaskViewSet,
    basename="kpi-task",
)

urlpatterns = router.urls
from rest_framework.routers import DefaultRouter

from .views import (
    BranchViewSet,
    DirectorateViewSet,
    DivisionViewSet,
    DepartmentViewSet,
    JobTitleViewSet,
)


router = DefaultRouter()

router.register(
    r"branches",
    BranchViewSet,
    basename="branch",
)

router.register(
    r"directorates",
    DirectorateViewSet,
    basename="directorate",
)

router.register(
    r"divisions",
    DivisionViewSet,
    basename="division",
)

router.register(
    r"departments",
    DepartmentViewSet,
    basename="department",
)

router.register(
    r"job-titles",
    JobTitleViewSet,
    basename="job-title",
)


urlpatterns = router.urls
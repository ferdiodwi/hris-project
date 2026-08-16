from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SalaryComponentViewSet


router = DefaultRouter()

router.register(
    r"salary-components",
    SalaryComponentViewSet,
    basename="salary-component"
)


urlpatterns = [
    path("", include(router.urls)),
]
from rest_framework import viewsets

from .models import SalaryComponent
from .serializers import SalaryComponentSerializer


class SalaryComponentViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryComponentSerializer

    def get_queryset(self):
        queryset = SalaryComponent.objects.all().order_by("id")

        employee_id = self.request.query_params.get(
            "employee_id"
        )

        component_type = self.request.query_params.get(
            "component_type"
        )

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        if component_type:
            queryset = queryset.filter(
                component_type=component_type
            )

        return queryset
from rest_framework import viewsets

from .models import ShiftMaster
from .serializers import ShiftMasterSerializer


class ShiftMasterViewSet(viewsets.ModelViewSet):
    queryset = ShiftMaster.objects.all().order_by("id")
    serializer_class = ShiftMasterSerializer
from core.base_views import CustomListAPIView
from repair.filters import DeviceFilter
from repair.models import RepairDeviceType
from repair.serializers import DeviceSerializer


class DeviceView(CustomListAPIView):
    serializer_class = DeviceSerializer
    queryset = RepairDeviceType.objects.filter(active=True)
    filterset_class = DeviceFilter
    pagination_class = None

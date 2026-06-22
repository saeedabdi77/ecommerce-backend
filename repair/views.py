from core.base_views import CustomListAPIView
from repair.models import RepairDeviceType
from repair.serializers import DeviceSerializer


class DeviceView(CustomListAPIView):
    serializer_class = DeviceSerializer
    queryset = RepairDeviceType.objects.filter(active=True)
    pagination_class = None

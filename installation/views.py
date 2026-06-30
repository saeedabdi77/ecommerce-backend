from core.base_views import CustomListAPIView
from installation.models import InstallationDeviceType
from installation.serializers import InstallationDeviceTypeSerializer


class InstallationDeviceTypeListView(CustomListAPIView):
    serializer_class = InstallationDeviceTypeSerializer
    queryset = InstallationDeviceType.objects.filter(active=True)
    pagination_class = None

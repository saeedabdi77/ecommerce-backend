from core.base_serializers import CustomModelSerializer
from installation.models import InstallationDeviceType


class InstallationDeviceTypeSerializer(CustomModelSerializer):
    class Meta:
        model = InstallationDeviceType
        fields = ('id', 'name')

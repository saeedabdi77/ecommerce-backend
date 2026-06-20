from core.base_serializers import CustomSerializer, CustomModelSerializer
from repair.models import RepairDeviceType


class DeviceSerializer(CustomModelSerializer):
    class Meta:
        model = RepairDeviceType
        fields = ('id', 'name')

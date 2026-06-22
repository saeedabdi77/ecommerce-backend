from core.base_serializers import CustomSerializer, CustomModelSerializer
from repair.models import RepairDeviceType, RepairProblemType


class DeviceSerializer(CustomModelSerializer):
    class Meta:
        model = RepairDeviceType
        fields = ('id', 'name')


class ProblemTypesSerializer(CustomModelSerializer):
    class Meta:
        model = RepairProblemType
        fields = ('id', 'name')

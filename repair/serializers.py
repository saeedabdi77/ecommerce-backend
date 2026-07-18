from core.base_serializers import CustomSerializer, CustomModelSerializer
from core.enums import SMSPatternType
from core.services import SMSService
from core.utilities import create_object
from repair.models import RepairDeviceType, RepairProblemType, RepairRequest


class DeviceSerializer(CustomModelSerializer):
    class Meta:
        model = RepairDeviceType
        fields = ('id', 'name')


class ProblemTypesSerializer(CustomModelSerializer):
    class Meta:
        model = RepairProblemType
        fields = ('id', 'name')


class RepairRequestCreateSerializer(CustomModelSerializer):

    class Meta:
        model = RepairRequest
        fields = ('name', 'phone_number', 'problem_type', 'device_type', 'description', 'image')

    def validate_serializer(self, attrs, error_obj):
        if self.context['request'].user.is_authenticated:
            attrs['user'] = self.context['request'].user

        return attrs

    def create(self, validated_data):
        create_object(RepairRequest, **validated_data)
        SMSService.notify_admins(
            SMSPatternType.NEW_REPAIR_REQUEST,
        )
        return validated_data

class RepairRequestRetrieveSerializer(CustomModelSerializer):

    class Meta:
        model = RepairRequest
        fields = ('name', 'phone_number', 'problem_type', 'device_type', 'description', 'image', 'status',
                  'estimated_price', 'final_price', 'admin_note')

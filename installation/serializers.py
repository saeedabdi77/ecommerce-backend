from core.base_serializers import CustomModelSerializer
from installation.models import InstallationDeviceType, Game, GameRate


class InstallationDeviceTypeSerializer(CustomModelSerializer):
    class Meta:
        model = InstallationDeviceType
        fields = ('id', 'name')


class GameRateSerializer(CustomModelSerializer):
    class Meta:
        model = GameRate
        fields = ('id', 'source', 'rate')

class GameSerializer(CustomModelSerializer):
    device_types = InstallationDeviceTypeSerializer(source='device_type', many=True)
    rates = GameRateSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'name', 'size', 'price', 'image', 'device_types', 'rates')

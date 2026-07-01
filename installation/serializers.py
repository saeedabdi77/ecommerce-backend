from rest_framework import serializers

from core.base_serializers import CustomModelSerializer
from installation.models import InstallationDeviceType, Game, GameRate, InstallationRequest, InstallationRequestItem


class InstallationDeviceTypeSerializer(CustomModelSerializer):
    class Meta:
        model = InstallationDeviceType
        fields = ('id', 'name')


class GameRateSerializer(CustomModelSerializer):
    class Meta:
        model = GameRate
        fields = ('id', 'source', 'rate')


class GameSerializer(CustomModelSerializer):
    device_type = InstallationDeviceTypeSerializer(many=True)
    rates = GameRateSerializer(many=True)

    class Meta:
        model = Game
        fields = ('id', 'name', 'size', 'price', 'image', 'device_type', 'rates')


class InstallationRequestItemGameSerializer(GameSerializer):
    class Meta:
        model = Game
        fields = ('id', 'name', 'size')


class InstallationRequestItemSerializer(CustomModelSerializer):
    game = InstallationRequestItemGameSerializer()

    class Meta:
        model = InstallationRequestItem
        fields = ('id', 'game', 'price')


class InstallationRequestRetrieveSerializer(CustomModelSerializer):
    device_type = InstallationDeviceTypeSerializer()
    clear_guest_uid = serializers.SerializerMethodField()
    items = InstallationRequestItemSerializer(many=True)

    class Meta:
        model = InstallationRequest
        fields = ('id', 'guest_uid', 'device_type', 'total_price', 'admin_note', 'clear_guest_uid', 'items', 'status')

    def get_clear_guest_uid(self, obj):
        return self.context['request'].query_params.get('guest_uid') and self.context['request'].user.is_authenticated

from rest_framework import serializers

from core.base_serializers import CustomModelSerializer
from core.utilities import create_object
from installation.models import InstallationDeviceType, Game, GameRate, InstallationRequest, InstallationRequestItem
from installation.utilities import get_or_create_draft_installation_request


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


class AddInstallationRequestItemSerializer(CustomModelSerializer):
    guest_uid = serializers.UUIDField(required=False, write_only=True)
    clear_guest_uid = serializers.SerializerMethodField()
    device_type = serializers.IntegerField(write_only=True)

    class Meta:
        model = InstallationRequestItem
        fields = ('id', 'game', 'guest_uid', 'clear_guest_uid', 'device_type')

    def get_clear_guest_uid(self, obj):
        return getattr(self, '_clear_guest_uid', False)

    def validate_serializer(self, attrs, error_obj):
        user = self.context['request'].user
        guest_uid = attrs.get('guest_uid')
        game = attrs.get('game')
        device_type_id = attrs.get('device_type')

        try:
            device_type = InstallationDeviceType.objects.get(id=device_type_id, active=True)
            attrs['device_type'] = device_type
        except InstallationDeviceType.DoesNotExist:
            error_obj.append_errors({
                "message": "دستگاه یافت نشد",
                "reason": "device_type"
            })
            return attrs

        draft_installation_request = get_or_create_draft_installation_request(device_type, user, guest_uid)
        attrs['installation_request'] = draft_installation_request
        if not draft_installation_request:
            error_obj.append_errors({
                "message": "ارسال شناسه کاربر یا شناسه مهمان الزامی است",
                "reason": "guest_uid"
            })

        if game:
            attrs['price'] = game.price

        if draft_installation_request and draft_installation_request.items.filter(game=game).exists():
            error_obj.append_errors({
                "message": "بازی از قبل انتخاب شده است",
                "reason": "game"
            })

        self._clear_guest_uid = bool(guest_uid and user and user.is_authenticated)
        return attrs

    def create(self, validated_data):
        return create_object(InstallationRequestItem, validated_data)

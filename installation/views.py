from django.http import Http404

from core.base_views import CustomListAPIView, CustomRetrieveAPIView
from installation.enums import InstallationRequestStatus
from installation.filters import GameFilter
from installation.models import InstallationDeviceType, Game, InstallationRequest
from installation.serializers import InstallationDeviceTypeSerializer, GameSerializer, \
    InstallationRequestRetrieveSerializer


class InstallationDeviceTypeListView(CustomListAPIView):
    serializer_class = InstallationDeviceTypeSerializer
    queryset = InstallationDeviceType.objects.filter(active=True)
    pagination_class = None


class GameListView(CustomListAPIView):
    serializer_class = GameSerializer
    filterset_class = GameFilter
    queryset = Game.objects.filter(active=True)


class DraftInstallationRequestRetrieveView(CustomRetrieveAPIView):
    serializer_class = InstallationRequestRetrieveSerializer

    def get_object(self):
        guest_uid = self.request.query_params.get('guest_uid')
        user = self.request.user

        if user.is_authenticated:
            request = user.installation_requests.filter(status=InstallationRequestStatus.DRAFT).first()
            if request:
                return request

        if guest_uid:
            request = InstallationRequest.objects.filter(status=InstallationRequestStatus.DRAFT, guest_uid=guest_uid,
                                                        user__isnull=True).first()
            if request:
                if user.is_authenticated:
                    request.user = user
                    request.save(update_fields=['user'])
                return request

        raise Http404

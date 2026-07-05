from django.http import Http404

from core.base_views import CustomListAPIView, CustomRetrieveAPIView
from installation.enums import InstallationRequestStatus
from installation.filters import GameFilter
from installation.models import InstallationDeviceType, Game, InstallationRequest
from installation.serializers import InstallationDeviceTypeSerializer, GameSerializer, \
    InstallationRequestRetrieveSerializer
from installation.utilities import resolve_draft_installation_request


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

        draft_installation_request = resolve_draft_installation_request(user, guest_uid)
        if draft_installation_request:
            return draft_installation_request
        raise Http404

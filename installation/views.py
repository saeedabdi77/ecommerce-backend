from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import Http404
from django.shortcuts import get_object_or_404

from core.base_views import CustomListAPIView, CustomRetrieveAPIView, CustomCreateAPIView, \
    CustomCreateListUpdateDestroyViewSet
from installation.enums import InstallationRequestStatus
from installation.filters import GameFilter
from installation.models import InstallationDeviceType, Game, InstallationRequest, InstallationRequestItem
from installation.serializers import InstallationDeviceTypeSerializer, GameSerializer, \
    InstallationRequestRetrieveSerializer, AddInstallationRequestItemSerializer
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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='guest_uid',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        guest_uid = self.request.query_params.get('guest_uid')
        user = self.request.user

        draft_installation_request = resolve_draft_installation_request(user, guest_uid)
        if draft_installation_request:
            return draft_installation_request
        raise Http404


class InstallationRequestItemViewSet(CustomCreateListUpdateDestroyViewSet):
    http_method_names = ("post", "delete")

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='guest_uid',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=False
            )
        ]
    )
    def delete(self, request, *args, **kwargs):
        return self.force_destroy(request, *args, **kwargs)

    def get_object(self):
        guest_uid = self.request.query_params.get('guest_uid')
        user = self.request.user
        pk = self.kwargs['pk']
        draft_installation_request = resolve_draft_installation_request(user, guest_uid)
        if draft_installation_request:
            return get_object_or_404(InstallationRequestItem, installation_request=draft_installation_request, id=pk)
        raise Http404

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddInstallationRequestItemSerializer

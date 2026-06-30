from core.base_views import CustomListAPIView
from installation.filters import GameFilter
from installation.models import InstallationDeviceType, Game
from installation.serializers import InstallationDeviceTypeSerializer, GameSerializer


class InstallationDeviceTypeListView(CustomListAPIView):
    serializer_class = InstallationDeviceTypeSerializer
    queryset = InstallationDeviceType.objects.filter(active=True)
    pagination_class = None


class GameListView(CustomListAPIView):
    serializer_class = GameSerializer
    filterset_class = GameFilter
    queryset = Game.objects.filter(active=True)

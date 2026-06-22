from core.base_views import CustomListAPIView
from repair.filters import RepairProblemTypeFilter
from repair.models import RepairDeviceType, RepairProblemType
from repair.serializers import DeviceSerializer, ProblemTypesSerializer


class DevicesListView(CustomListAPIView):
    serializer_class = DeviceSerializer
    queryset = RepairDeviceType.objects.filter(active=True)
    pagination_class = None


class ProblemTypesListView(CustomListAPIView):
    serializer_class = ProblemTypesSerializer
    queryset = RepairProblemType.objects.filter(active=True)
    filterset_class = RepairProblemTypeFilter
    pagination_class = None



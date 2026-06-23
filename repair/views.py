from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.base_views import CustomListAPIView, CustomCreateListViewSet
from repair.filters import RepairProblemTypeFilter
from repair.models import RepairDeviceType, RepairProblemType, RepairRequest
from repair.serializers import DeviceSerializer, ProblemTypesSerializer, RepairRequestCreateSerializer, \
    RepairRequestRetrieveSerializer


class DevicesListView(CustomListAPIView):
    serializer_class = DeviceSerializer
    queryset = RepairDeviceType.objects.filter(active=True)
    pagination_class = None


class ProblemTypesListView(CustomListAPIView):
    serializer_class = ProblemTypesSerializer
    queryset = RepairProblemType.objects.filter(active=True)
    filterset_class = RepairProblemTypeFilter
    pagination_class = None


class RepairRequestViewSet(CustomCreateListViewSet):
    http_method_names = ('post', 'get')
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return RepairRequest.objects.filter(user=self.request.user)
        return RepairRequest.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RepairRequestCreateSerializer
        else:
            return RepairRequestRetrieveSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return (IsAuthenticated(),)
        return (AllowAny(),)

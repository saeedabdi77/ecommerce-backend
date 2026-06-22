from django_filters import rest_framework as filters
from repair.models import RepairDeviceType, RepairProblemType


class RepairProblemTypeFilter(filters.FilterSet):
    devices = filters.BaseInFilter(field_name='device_types__id', lookup_expr='in')

    class Meta:
        model = RepairProblemType
        fields = ('devices',)

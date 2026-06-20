from django_filters import rest_framework as filters
from repair.models import RepairDeviceType

class DeviceFilter(filters.FilterSet):
    ids = filters.BaseInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = RepairDeviceType
        fields = ('ids',)

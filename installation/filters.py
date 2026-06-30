import django_filters
from installation.models import Game

class GameFilter(django_filters.FilterSet):
    device_type = django_filters.BaseInFilter(field_name='device_type', lookup_expr='in')

    class Meta:
        model = Game
        fields = ('device_type',)

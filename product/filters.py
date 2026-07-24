from django_filters import rest_framework as filters
from product.models import Brand, Category


class BrandFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Brand
        fields = {
            'name': ['icontains', 'exact'],
        }


class CategoryFilter(filters.FilterSet):
    search = filters.CharFilter(field_name='name', lookup_expr='icontains')
    homepage_show = filters.BooleanFilter(field_name='homepage_show', lookup_expr='exact')

    class Meta:
        model = Category
        fields = {
            'name': ['icontains', 'exact'],
            'homepage_show': ['exact'],
            'order': ['exact', 'gte', 'lte'],
        }

from django_filters import rest_framework as filters
from django.db.models import Q
from product.models import Brand, Category, ProductType


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


class ProductFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    category = filters.NumberFilter(field_name='category__id', lookup_expr='exact')
    category_slug = filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    brand = filters.NumberFilter(field_name='brand__id', lookup_expr='exact')
    brand_slug = filters.CharFilter(field_name='brand__slug', lookup_expr='exact')
    collection = filters.CharFilter(method='filter_by_collection')
    min_price = filters.NumberFilter(field_name='sell_price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='sell_price', lookup_expr='lte')
    has_stock = filters.BooleanFilter(method='filter_has_stock')
    has_discount = filters.BooleanFilter(method='filter_has_discount')
    tags = filters.CharFilter(method='filter_by_tags')
    attributes = filters.CharFilter(method='filter_by_attributes')

    class Meta:
        model = ProductType
        fields = {
            'name': ['icontains', 'exact'],
            'slug': ['exact'],
            'created_at': ['gte', 'lte'],
        }

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(slug__icontains=value) |
            Q(tags__name__icontains=value) |
            Q(category__name__icontains=value) |
            Q(brand__name__icontains=value)
        ).distinct()

    def filter_by_collection(self, queryset, name, value):
        return queryset.filter(collections__code_name=value, collections__is_active=True).distinct()

    def filter_has_stock(self, queryset, name, value):
        if value:
            return queryset.filter(products__state='in_warehouse').distinct()
        return queryset

    def filter_has_discount(self, queryset, name, value):
        # TODO: Implement discount checking when discount model is added
        return queryset

    def filter_by_tags(self, queryset, name, value):
        tags = value.split(',')
        return queryset.filter(tags__slug__in=tags).distinct()

    def filter_by_attributes(self, queryset, name, value):
        # Format: attribute_value_slug,attribute_value_slug
        # Example: ?attributes=color-black,storage-256gb
        attribute_values = value.split(',')
        return queryset.filter(product_attributes__attribute_value__slug__in=attribute_values).distinct()

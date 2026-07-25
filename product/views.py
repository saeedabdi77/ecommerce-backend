from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from core.base_views import CustomListAPIView
from product.filters import BrandFilter, CategoryFilter, ProductFilter
from product.models import Brand, Category, ProductType
from product.serializers import BrandSerializer, CategorySerializer, ProductListSerializer


class BrandListView(CustomListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.filter(is_active=True)
    filterset_class = BrandFilter
    pagination_class = None
    permission_classes = (AllowAny,)


class CategoryListView(CustomListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    filterset_class = CategoryFilter
    pagination_class = None
    permission_classes = (AllowAny,)


class ProductListView(CustomListAPIView):
    serializer_class = ProductListSerializer
    queryset = ProductType.objects.filter(active=True).select_related('category', 'brand').prefetch_related('images',
                                                                                                            'tags',
                                                                                                            'attributes',
                                                                                                            'attributes__attribute',
                                                                                                            'products')
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ('sell_price', 'main_price', 'created_at', 'order')
    ordering = ('-created_at',)
    permission_classes = (AllowAny,)

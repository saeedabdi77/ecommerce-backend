from rest_framework.permissions import AllowAny

from core.base_views import CustomListAPIView
from product.filters import BrandFilter, CategoryFilter
from product.models import Brand, Category
from product.serializers import BrandSerializer, CategorySerializer


class BrandListView(CustomListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.filter(is_active=True)
    filterset_class = BrandFilter
    pagination_class = None
    permission_classes = (AllowAny,)


class CategoryListView(CustomListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True)
    filterset_class = CategoryFilter
    pagination_class = None
    permission_classes = (AllowAny,)

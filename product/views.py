from django.db.models import Exists, OuterRef
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import status

from core.base_views import CustomListAPIView, CustomRetrieveAPIView
from product.activity import enqueue_catalog_activity
from product.enums import CatalogActivityEvent, ProductState
from product.filters import BrandFilter, CategoryFilter, ProductFilter
from product.models import Brand, Category, Product, ProductType
from product.serializers import BrandSerializer, CategorySerializer, ProductDetailSerializer, ProductListSerializer


def _is_first_page(request):
    page = request.query_params.get('page')
    if page in (None, '', '1'):
        return True
    try:
        return int(page) <= 1
    except (TypeError, ValueError):
        return True


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

    def get_queryset(self):
        return super().get_queryset().annotate(
            has_stock=Exists(
                Product.objects.filter(
                    product_type_id=OuterRef('pk'),
                    state=ProductState.IN_WAREHOUSE,
                )
            ),
        )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.order_by('-has_stock', *queryset.query.order_by)

    def list(self, request, *args, **kwargs):
        self._enqueue_list_activity(request)
        return super().list(request, *args, **kwargs)

    def _enqueue_list_activity(self, request):
        if not _is_first_page(request):
            return

        search = (request.query_params.get('search') or '').strip()
        if search:
            enqueue_catalog_activity(request, CatalogActivityEvent.SEARCH, query=search[:255])

        category_id = request.query_params.get('category')
        category_slug = request.query_params.get('category_slug')
        if not category_id and not category_slug:
            return

        category = None
        if category_id:
            category = Category.objects.filter(pk=category_id).first()
        elif category_slug:
            category = Category.objects.filter(slug=category_slug).first()

        if category is not None:
            enqueue_catalog_activity(
                request,
                CatalogActivityEvent.CATEGORY_VIEW,
                category_id=category.pk,
            )


class ProductDetailView(CustomRetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = (AllowAny,)
    queryset = ProductType.objects.filter(active=True).select_related('category', 'brand').prefetch_related(
        'images',
        'tags',
        'attributes',
        'attributes__attribute',
        'products',
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        enqueue_catalog_activity(
            request,
            CatalogActivityEvent.PRODUCT_VIEW,
            product_type_id=instance.pk,
        )
        serializer = self.get_serializer(instance)
        return Response(
            {'message': "Instance retrieved successfully", 'data': serializer.data},
            status=status.HTTP_200_OK,
        )

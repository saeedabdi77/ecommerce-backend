from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.base_views import CustomRetrieveAPIView, CustomCreateListUpdateDestroyViewSet
from order.models import OrderItemProduct, OrderItem
from order.serializers import OrderRetrieveSerializer, AddCartItemSerializer
from order.utilities import resolve_draft_order
from product.enums import ProductState


class CartRetrieveView(CustomRetrieveAPIView):
    serializer_class = OrderRetrieveSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='guest_uid',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=False
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        guest_uid = self.request.query_params.get('guest_uid')
        user = self.request.user

        draft_order = resolve_draft_order(user, guest_uid)
        if draft_order:
            return draft_order
        raise Http404


class CartItemViewSet(CustomCreateListUpdateDestroyViewSet):
    http_method_names = ("post", "delete")

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="guest_uid",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=False
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        order = instance.order

        with transaction.atomic():
            item_products = OrderItemProduct.objects.filter(
                order_item=instance
            ).select_related("product")

            for item_product in item_products:
                product = item_product.product
                product.state = ProductState.IN_WAREHOUSE
                product.save(update_fields=["state"])

            item_products.force_delete()

            instance.force_delete()

            if not order.items.exists():
                order.force_delete()
            else:
                order.calculate_total_price()

        return Response(
            {"message": "Instance delete successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=("delete",))
    def decrease(self, request, *args, **kwargs):
        instance = self.get_object()
        order = instance.order

        with transaction.atomic():
            order_item_product = OrderItemProduct.objects.filter(order_item=instance).select_related("product").last()

            if not order_item_product:
                raise Http404

            product = order_item_product.product
            product.state = ProductState.IN_WAREHOUSE
            product.save(update_fields=("state",))

            order_item_product.force_delete()

            instance.count -= 1

            if instance.count <= 0:
                instance.force_delete()

                if not order.items.exists():
                    order.force_delete()
                else:
                    order.calculate_total_price()
            else:
                instance.save(update_fields=("count",))

        return Response(
            {"message": "Item decreased successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    def get_object(self):
        guest_uid = self.request.data.get("guest_uid") or self.request.query_params.get("guest_uid")
        user = self.request.user
        pk = self.kwargs["pk"]

        draft_order = resolve_draft_order(user, guest_uid)

        if draft_order:
            return get_object_or_404(OrderItem, order=draft_order, id=pk)

        raise Http404

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer

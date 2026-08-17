from django.db import transaction
from rest_framework import serializers

from core.base_serializers import CustomModelSerializer
from core.utilities import create_object
from order.models import Order, OrderItem
from order.utilities import get_or_create_draft_order, sync_draft_order
from product.enums import ProductState
from product.models import ProductType


class OrderItemProductTypeSerializer(CustomModelSerializer):
    class Meta:
        model = ProductType
        fields = ("id", "name", "slug")


class OrderItemSerializer(CustomModelSerializer):
    product_type = OrderItemProductTypeSerializer()

    class Meta:
        model = OrderItem
        fields = ("id", "product_type", "count", "price")


class OrderRetrieveSerializer(CustomModelSerializer):
    clear_guest_uid = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "guest_uid", "total_price", "admin_note", "clear_guest_uid", "items", "status",)

    def get_clear_guest_uid(self, obj):
        return bool(
            self.context["request"].query_params.get("guest_uid") and self.context["request"].user.is_authenticated)


class AddCartItemSerializer(CustomModelSerializer):
    product_type = serializers.PrimaryKeyRelatedField(queryset=ProductType.objects.filter(active=True), write_only=True)
    guest_uid = serializers.UUIDField(required=False, write_only=True)
    clear_guest_uid = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ("id", "product_type", "guest_uid", "clear_guest_uid")

    def get_clear_guest_uid(self, obj):
        return getattr(self, "_clear_guest_uid", False)

    def validate_serializer(self, attrs, error_obj):
        user = self.context["request"].user
        guest_uid = attrs.get("guest_uid")
        product_type = attrs.get("product_type")

        order = get_or_create_draft_order(user=user, guest_uid=guest_uid)

        if not order:
            error_obj.append_errors({
                "message": "ارسال شناسه کاربر یا شناسه مهمان الزامی است",
                "reason": "guest_uid"
            })
            return attrs

        order_item = order.items.filter(product_type=product_type).first()
        available_count = product_type.products.filter(state=ProductState.IN_WAREHOUSE).count()

        if order_item and order_item.count >= available_count:
            error_obj.append_errors({
                "message": "موجودی این محصول کافی نیست",
                "reason": "product_type"
            })
            sync_draft_order(order_item.order)

        elif not product_type.products.filter(state=ProductState.IN_WAREHOUSE).exists():
            error_obj.append_errors({
                "message": "این محصول موجود نیست",
                "reason": "product_type"
            })
            sync_draft_order(order)

        attrs["order"] = order
        attrs["price"] = product_type.sell_price

        self._clear_guest_uid = bool(guest_uid and user and user.is_authenticated)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        order = validated_data["order"]
        product_type = validated_data["product_type"]

        order_item = order.items.filter(product_type=product_type).first()

        if order_item:
            order_item.count += 1
            order_item.save(update_fields=("count",))
        else:
            order_item = create_object(OrderItem, validated_data)

        order.calculate_total_price()

        return order_item

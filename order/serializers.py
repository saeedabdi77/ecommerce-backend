from django.db import transaction
from rest_framework import serializers

from core.base_serializers import CustomModelSerializer, CustomSerializer
from core.utilities import create_object
from order.models import Order, OrderItem, DeliveryMethod
from order.utilities import get_or_create_draft_order, sync_draft_order, calculate_delivery_method_cost, \
    get_available_delivery_methods
from product.enums import ProductState
from product.models import ProductType
from user.models import Address
from user.serializers import GetAddressSerializer


class OrderItemProductTypeSerializer(CustomModelSerializer):
    class Meta:
        model = ProductType
        fields = ("id", "name", "slug")


class OrderItemSerializer(CustomModelSerializer):
    product_type = OrderItemProductTypeSerializer()

    class Meta:
        model = OrderItem
        fields = ("id", "product_type", "count", "price")


class DeliveryMethodSerializer(CustomModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = ("id", "name", "description", "is_active", "is_tehran_city_only", "delivery_time")


class OrderRetrieveSerializer(CustomModelSerializer):
    clear_guest_uid = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True)
    delivery_address = GetAddressSerializer(read_only=True)
    delivery_method = DeliveryMethodSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ("id", "guest_uid", "total_price", "admin_note", "clear_guest_uid", "items", "status", "delivery_address",
            "delivery_method", "delivery_cost")

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

        elif not available_count:
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


class SelectDeliveryAddressSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        if not Address.objects.filter(
            id=value,
            user=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError("آدرس معتبر نیست.")

        return value

    def update(self, instance, validated_data):
        instance.delivery_address_id = validated_data["address_id"]
        instance.delivery_method = None
        instance.delivery_cost = 0
        instance.save(update_fields=[
            "delivery_address",
            "delivery_method",
            "delivery_cost",
        ])
        return instance


class DeliveryMethodListSerializer(CustomModelSerializer):
    cost = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryMethod
        fields = ("id", "name", "description", "delivery_time", "cost")

    def get_cost(self, obj):
        return calculate_delivery_method_cost(self.context["order"], obj)


class SelectDeliveryMethodSerializer(CustomSerializer):
    delivery_method_id = serializers.IntegerField()

    def validate_serializer(self, attrs, error_obj):
        order = self.instance

        if not order.delivery_address:
            error_obj.append_errors({"message": "ابتدا آدرس ارسال را انتخاب کنید.", "reason": "delivery_address"})

        delivery_method = get_available_delivery_methods(order).filter(id=attrs["delivery_method_id"]).first()

        if not delivery_method:
            error_obj.append_errors({"message": "روش ارسال معتبر نیست.", "reason": "delivery_method_id"})

        attrs["delivery_method"] = delivery_method
        return attrs

    def update(self, instance, validated_data):
        delivery_method = validated_data["delivery_method"]
        instance.delivery_method = delivery_method
        instance.delivery_cost = calculate_delivery_method_cost(instance, delivery_method)
        instance.save(update_fields=("delivery_method", "delivery_cost"))
        return instance

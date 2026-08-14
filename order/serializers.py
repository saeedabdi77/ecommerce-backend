from rest_framework import serializers

from core.base_serializers import CustomModelSerializer
from order.models import Order, OrderItem
from product.models import Product, ProductType


class OrderItemProductTypeSerializer(CustomModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'name', 'slug')


class OrderItemProductSerializer(CustomModelSerializer):
    product_type = OrderItemProductTypeSerializer()

    class Meta:
        model = Product
        fields = ('id', 'product_type', 'serial')


class OrderItemSerializer(CustomModelSerializer):
    product = OrderItemProductSerializer()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'price')


class OrderRetrieveSerializer(CustomModelSerializer):
    clear_guest_uid = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'guest_uid', 'total_price', 'admin_note', 'clear_guest_uid', 'items', 'status')

    def get_clear_guest_uid(self, obj):
        return self.context['request'].query_params.get('guest_uid') and self.context['request'].user.is_authenticated

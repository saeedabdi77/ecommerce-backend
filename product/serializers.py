from rest_framework import serializers

from core.base_serializers import CustomModelSerializer
from product.models import Brand, Category


class BrandSerializer(CustomModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'logo')


class CategorySerializer(CustomModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'image', 'icon', 'homepage_show', 'order', 'children')

    @staticmethod
    def get_children(obj):
        serializer = CategorySerializer(obj.children.all(), many=True)
        return serializer.data

from rest_framework import serializers

from core.base_serializers import CustomModelSerializer
from product.models import Brand, Category, ProductImage, Tag, AttributeValue, ProductType


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


class ProductImageSerializer(CustomModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_thumbnail', 'order', 'alt_text')


class TagSerializer(CustomModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class AttributeValueSerializer(CustomModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ('id', 'value', 'slug', 'attribute')


class ProductListSerializer(CustomModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    attributes = AttributeValueSerializer(many=True, read_only=True, source='attributes')
    stock = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = ProductType
        fields = ('id', 'name', 'slug', 'description', 'main_price', 'sell_price', 'stock', 'category', 'category_name',
                  'brand', 'brand_name', 'images', 'tags', 'attributes', 'active', 'created_at')

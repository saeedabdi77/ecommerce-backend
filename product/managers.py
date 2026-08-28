from django.db.models import Count, Q, Sum
from django.urls import reverse

from core.manager.actions import CreateAction, DeleteAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.filters import BooleanFilter, ChoiceFilter, DateFilter, ForeignKeyFilter, TextFilter
from core.manager.managers import BaseManager, registry
from product.enums import ProductState
from product.forms import (
    AttributeForm,
    AttributeValueForm,
    BrandForm,
    CategoryForm,
    ProductAttributeForm,
    ProductCollectionForm,
    ProductForm,
    ProductImageForm,
    ProductTypeForm,
    ReviewForm,
    TagForm,
)
from product.models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductCollection,
    ProductImage,
    ProductType,
    Review,
    Tag,
)


@registry.register
class CategoryManager(BaseManager):
    slug = "categories"
    model = Category

    menu_group = "product_management"
    menu_label = "دسته‌بندی‌ها"
    menu_icon = "folder"
    menu_order = 10

    columns = (
        Column("name", "نام", sortable=True),
        Column("parent", "والد", sortable=True),
        Column("children_count", "زیرمجموعه", sortable=True),
        Column("homepage_show", "صفحه اصلی", sortable=True, editable=True),
        Column("order", "ترتیب", sortable=True, editable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        ForeignKeyFilter("parent", queryset=Category.objects.all(), label="دسته بندی پدر"),
        BooleanFilter("homepage_show", "نمایش در صفحه اصلی"),
    )

    actions = (
        CreateAction(CategoryForm),
        DetailAction(),
        UpdateAction(CategoryForm),
        DeleteAction(),
    )

    search_fields = ("name", "slug")
    ordering = ("order", "name")
    select_related = ("parent",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            children_count=Count("children", distinct=True),
        )


@registry.register
class BrandManager(BaseManager):
    slug = "brands"
    model = Brand

    menu_group = "product_management"
    menu_label = "برندها"
    menu_icon = "tag"
    menu_order = 20

    columns = (
        Column("name", "نام", sortable=True),
        Column("slug", "اسلاگ", sortable=True),
        Column("product_types_count", "تعداد محصولات", sortable=True),
        Column("is_active", "فعال", sortable=True, editable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        BooleanFilter("is_active", "فعال"),
    )

    actions = (
        CreateAction(BrandForm),
        DetailAction(),
        UpdateAction(BrandForm),
        DeleteAction(),
    )

    search_fields = ("name", "slug")
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_types_count=Count("product_types", distinct=True),
        )


@registry.register
class AttributeManager(BaseManager):
    slug = "attributes"
    model = Attribute

    menu_group = "product_management"
    menu_label = "ویژگی‌ها"
    menu_icon = "sliders"
    menu_order = 30

    columns = (
        Column("name", "نام", sortable=True),
        Column("slug", "اسلاگ", sortable=True),
        Column("values_count", "تعداد مقادیر", sortable=True),
    )

    filters = (
        TextFilter("name", "نام"),
    )

    actions = (
        CreateAction(AttributeForm),
        DetailAction(),
        UpdateAction(AttributeForm),
        DeleteAction(),
    )

    search_fields = ("name", "slug")
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            values_count=Count("values", distinct=True),
        )


@registry.register
class AttributeValueManager(BaseManager):
    slug = "attribute-values"
    model = AttributeValue

    menu_group = "product_management"
    menu_label = "مقادیر ویژگی"
    menu_icon = "list"
    menu_order = 40

    columns = (
        Column("attribute.name", "ویژگی", sortable=True),
        Column("value", "مقدار", sortable=True),
        Column("slug", "اسلاگ", sortable=True),
    )

    filters = (
        TextFilter("value", "مقدار"),
        ForeignKeyFilter("attribute", queryset=Attribute.objects.all(), label="ویژگی"),
    )

    actions = (
        CreateAction(AttributeValueForm),
        DetailAction(),
        UpdateAction(AttributeValueForm),
        DeleteAction(),
    )

    search_fields = ("value", "slug", "attribute__name")
    ordering = ("attribute__name", "value")

    select_related = ("attribute",)


@registry.register
class TagManager(BaseManager):
    slug = "tags"
    model = Tag

    menu_group = "product_management"
    menu_label = "برچسب‌ها"
    menu_icon = "tag"
    menu_order = 50

    columns = (
        Column("name", "برچسب", sortable=True),
        Column("slug", "اسلاگ", sortable=True),
        Column("product_types_count", "تعداد محصولات", sortable=True),
    )

    filters = (
        TextFilter("name", "برچسب"),
    )

    actions = (
        CreateAction(TagForm),
        DetailAction(),
        UpdateAction(TagForm),
        DeleteAction(),
    )

    search_fields = ("name", "slug")
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_types_count=Count("product_types", distinct=True),
        )


@registry.register
class ProductTypeManager(BaseManager):
    slug = "product-types"
    model = ProductType

    menu_group = "product_management"
    menu_label = "انواع محصول"
    menu_icon = "box"
    menu_order = 60

    columns = (
        Column("name", "نام محصول", sortable=True),
        Column("category", "دسته بندی", sortable=True),
        Column("brand", "برند"),
        Column("sell_price", "قیمت فروش", sortable=True, editable=True),
        Column("stock_count", "موجودی", sortable=True),
        Column("active", "فعال", sortable=True, editable=True),
    )

    filters = (
        TextFilter("name", "نام محصول"),
        BooleanFilter("active", "فعال"),
        ForeignKeyFilter("category", queryset=Category.objects.all(), label="دسته بندی"),
        ForeignKeyFilter("brand", queryset=Brand.objects.all(), label="برند"),
    )

    actions = (
        CreateAction(ProductTypeForm),
        DetailAction(),
        UpdateAction(ProductTypeForm),
        DeleteAction(),
    )

    search_fields = ("name", "slug", "category__name", "brand__name")
    search_placeholder = "نام، اسلاگ، دسته‌بندی، برند"
    ordering = ("-id",)

    select_related = ("category", "brand")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            stock_count=Count(
                "products",
                filter=Q(products__state="IN_WAREHOUSE"),
                distinct=True,
            ),
        )


@registry.register
class ProductAttributeManager(BaseManager):
    slug = "product-attributes"
    model = ProductAttribute

    menu_group = "product_management"
    menu_label = "ویژگی‌های محصول"
    menu_icon = "sliders"
    menu_order = 70

    columns = (
        Column("product_type.name", "محصول", sortable=True),
        Column("attribute_value.attribute.name", "ویژگی", sortable=True),
        Column("attribute_value.value", "مقدار", sortable=True),
        Column("extra_price", "قیمت اضافه", sortable=True, editable=True),
    )

    filters = (
        TextFilter("attribute_value__value", "مقدار"),
        ForeignKeyFilter("product_type", queryset=ProductType.objects.all(), label="محصول"),
        ForeignKeyFilter("attribute_value", queryset=AttributeValue.objects.select_related("attribute").all(), label="مقدار ویژگی"),
    )

    actions = (
        CreateAction(ProductAttributeForm),
        DetailAction(),
        UpdateAction(ProductAttributeForm),
        DeleteAction(),
    )

    search_fields = (
        "product_type__name",
        "attribute_value__value",
        "attribute_value__attribute__name",
    )

    ordering = ("product_type__name", "attribute_value__attribute__name")

    select_related = (
        "product_type",
        "attribute_value__attribute",
    )


@registry.register
class ProductImageManager(BaseManager):
    slug = "product-images"
    model = ProductImage

    menu_group = "product_management"
    menu_label = "تصاویر محصول"
    menu_icon = "image"
    menu_order = 80

    columns = (
        Column("product_type.name", "محصول", sortable=True),
        Column("image", "تصویر"),
        Column("is_thumbnail", "تصویر اصلی", sortable=True, editable=True),
        Column("order", "ترتیب", sortable=True, editable=True),
    )

    filters = (
        ForeignKeyFilter("product_type", queryset=ProductType.objects.all(), label="محصول"),
        BooleanFilter("is_thumbnail", "تصویر اصلی"),
    )

    actions = (
        CreateAction(ProductImageForm),
        DetailAction(),
        UpdateAction(ProductImageForm),
        DeleteAction(),
    )

    ordering = ("order",)
    select_related = ("product_type",)


@registry.register
class ProductManager(BaseManager):
    slug = "products"
    model = Product

    menu_group = "inventory"
    menu_label = "محصولات"
    menu_icon = "package"
    menu_order = 10

    columns = (
        Column("id", "شناسه", sortable=True),
        Column("product_type.name", "محصول", sortable=True),
        Column("product_type.category", "دسته بندی", sortable=True),
        Column("serial", "سریال", sortable=True),
        Column("purchase_price", "قیمت خرید", sortable=True, editable=True),
        Column("state", "وضعیت", sortable=True, editable=True),
    )

    filters = (
        TextFilter("serial", "سریال"),
        ForeignKeyFilter("product_type", queryset=ProductType.objects.all(), label="نوع محصول"),
        ChoiceFilter("state", ProductState.choices, label="وضعیت"),
    )

    actions = (
        CreateAction(ProductForm),
        DetailAction(),
        UpdateAction(ProductForm),
        DeleteAction(),
    )

    search_fields = (
        "serial",
        "product_type__name",
        "product_type__slug",
    )
    search_placeholder = "سریال، نام محصول"
    ordering = ("-id",)

    select_related = (
        "product_type",
        "product_type__category",
        "product_type__brand",
    )



@registry.register
class ReviewManager(BaseManager):
    slug = "reviews"
    model = Review

    menu_group = "customers"
    menu_label = "نظرات"
    menu_icon = "message"
    menu_order = 20

    columns = (
        Column("product_type.name", "محصول", sortable=True),
        Column("user.username", "کاربر", sortable=True),
        Column("rating", "امتیاز", sortable=True),
        Column("title", "عنوان"),
        Column("is_verified", "تایید شده", sortable=True, editable=True),
        Column("is_approved", "منتشر شده", sortable=True, editable=True),
        Column("created_at", "تاریخ", sortable=True),
    )

    filters = (
        ForeignKeyFilter("product_type", queryset=ProductType.objects.all(), label="محصول"),
        BooleanFilter("is_verified", "تایید شده"),
        BooleanFilter("is_approved", "منتشر شده"),
    )

    actions = (
        DetailAction(),
        UpdateAction(ReviewForm),
        DeleteAction(),
    )

    search_fields = (
        "title",
        "comment",
        "user__username",
        "product_type__name",
    )

    ordering = ("-created_at",)

    select_related = (
        "user",
        "product_type",
    )



@registry.register
class ProductCollectionManager(BaseManager):
    slug = "collections"
    model = ProductCollection

    menu_group = "product_management"
    menu_label = "مجموعه‌ها"
    menu_icon = "layers"
    menu_order = 90

    columns = (
        Column("name", "نام", sortable=True),
        Column("code_name", "کد", sortable=True),
        Column("product_types_count", "تعداد محصولات", sortable=True),
        Column("is_active", "فعال", sortable=True, editable=True),
        Column("order", "ترتیب", sortable=True, editable=True),
    )

    filters = (
        TextFilter("name", "نام"),
        BooleanFilter("is_active", "فعال"),
    )

    actions = (
        CreateAction(ProductCollectionForm),
        DetailAction(),
        UpdateAction(ProductCollectionForm),
        DeleteAction(),
    )

    search_fields = ("name", "code_name")
    ordering = ("order", "name")

    prefetch_related = ("product_types",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_types_count=Count("product_types", distinct=True),
        )

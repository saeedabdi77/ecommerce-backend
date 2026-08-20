from core.manager.actions import CreateAction, DeleteAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.filters import BooleanFilter, ForeignKeyFilter, TextFilter
from core.manager.managers import BaseManager, registry
from product.forms import ProductTypeForm, CategoryForm, BrandForm
from product.models import ProductType, Category, Brand


@registry.register
class ProductTypeManager(BaseManager):
    slug = "product-types"
    model = ProductType

    columns = (
        Column("name", "نام محصول", sortable=True),
        Column("category", "دسته بندی", sortable=True),
        Column("brand", "برند"),
        Column("main_price", "قیمت اصلی", sortable=True),
        Column("sell_price", "قیمت فروش", sortable=True),
        Column("active", "فعال", sortable=True),
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

    search_fields = ("name", "slug")
    ordering = ("-id",)

    select_related = ("category", "brand")


@registry.register
class CategoryManager(BaseManager):
    slug = "categories"
    model = Category
    columns = [
        Column("name", "نام"),
        Column("parent", "دسته بندی پدر"),
        Column("homepage_show", "نمایش در صفحه اصلی"),
        Column("order", "ترتیب"),
    ]
    filters = [
        TextFilter("name", "نام"),
        ForeignKeyFilter("parent", queryset=Category.objects.all(), label="دسته بندی پدر"),
        BooleanFilter("homepage_show", "نمایش در صفحه اصلی"),
    ]
    actions = [
        CreateAction(CategoryForm),
        DetailAction(),
        UpdateAction(CategoryForm),
        DeleteAction(),
    ]
    ordering = ("order", "name")


@registry.register
class BrandManager(BaseManager):
    slug = "brands"
    model = Brand
    columns = [
        Column("name", "نام"),
        Column("slug", "اسلاگ"),
        Column("is_active", "فعال"),
    ]
    filters = [
        TextFilter("name", "نام"),
        BooleanFilter("is_active", "فعال"),
    ]
    actions = [
        CreateAction(BrandForm),
        DetailAction(),
        UpdateAction(BrandForm),
        DeleteAction(),
    ]
    ordering = ("name",)
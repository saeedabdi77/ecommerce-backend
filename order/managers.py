from core.manager.actions import CreateAction, DeleteAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.filters import ChoiceFilter, ForeignKeyFilter, TextFilter
from core.manager.managers import BaseManager, registry
from order.forms import OrderForm, OrderItemForm, OrderItemProductForm
from order.models import Order, OrderItem, OrderItemProduct
from product.models import Product, ProductType
from user.models import User


@registry.register
class OrderManager(BaseManager):
    slug = "orders"
    model = Order

    menu_group = "orders"
    menu_label = "سفارش‌ها"
    menu_icon = "order"
    menu_order = 10

    columns = (
        Column("tracking_code", "کد پیگیری", sortable=True),
        Column("user", "کاربر", sortable=True),
        Column("status", "وضعیت", sortable=True, editable=True),
        Column("total_price", "مبلغ کل", sortable=True),
        Column("created_at", "تاریخ ثبت", sortable=True),
    )

    filters = (
        TextFilter("tracking_code", "کد پیگیری", lookup="exact"),
        ForeignKeyFilter("user", queryset=User.objects.all(), label="کاربر"),
        ChoiceFilter.from_field(Order, "status", label="وضعیت"),
    )

    actions = (
        CreateAction(OrderForm),
        DetailAction(),
        UpdateAction(OrderForm),
        DeleteAction(),
    )

    search_fields = ("tracking_code", "user__phone_number", "user__first_name", "user__last_name")
    ordering = ("-created_at",)

    select_related = ("user",)


@registry.register
class OrderItemManager(BaseManager):
    slug = "order-items"
    model = OrderItem

    menu_group = "orders"
    menu_label = "آیتم‌های سفارش"
    menu_icon = "list"
    menu_order = 20

    columns = (
        Column("order.tracking_code", "کد پیگیری", sortable=True),
        Column("product_type.name", "محصول", sortable=True),
        Column("count", "تعداد", sortable=True, editable=True),
        Column("price", "قیمت", sortable=True, editable=True),
    )

    filters = (
        ForeignKeyFilter("order", queryset=Order.objects.all(), label="سفارش"),
        ForeignKeyFilter("product_type", queryset=ProductType.objects.all(), label="محصول"),
    )

    actions = (
        CreateAction(OrderItemForm),
        DetailAction(),
        UpdateAction(OrderItemForm),
        DeleteAction(),
    )

    search_fields = ("order__tracking_code", "product_type__name")
    ordering = ("-created_at",)

    select_related = ("order", "product_type")


@registry.register
class OrderItemProductManager(BaseManager):
    slug = "order-item-products"
    model = OrderItemProduct

    menu_group = "orders"
    menu_label = "کالاهای سفارش"
    menu_icon = "box"
    menu_order = 30

    columns = (
        Column("order_item.order.tracking_code", "کد پیگیری", sortable=True),
        Column("order_item.product_type.name", "محصول", sortable=True),
        Column("product.serial", "سریال", sortable=True),
    )

    filters = (
        ForeignKeyFilter("order_item", queryset=OrderItem.objects.select_related("order", "product_type").all(), label="آیتم سفارش"),
        ForeignKeyFilter("product", queryset=Product.objects.all(), label="کالا"),
    )

    actions = (
        CreateAction(OrderItemProductForm),
        DetailAction(),
        UpdateAction(OrderItemProductForm),
        DeleteAction(),
    )

    search_fields = ("order_item__order__tracking_code", "order_item__product_type__name", "product__serial")
    ordering = ("-created_at",)

    select_related = ("order_item", "order_item__order", "order_item__product_type", "product", "product__product_type")

from core.manager.actions import CreateAction, DeleteAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.filters import BooleanFilter, ChoiceFilter, ForeignKeyFilter, TextFilter
from core.manager.inlines import Inline
from core.manager.managers import BaseManager, registry
from order.forms import (
    DeliveryMethodForm,
    DeliveryPricingInlineForm,
    OrderConfigForm,
    OrderForm,
    OrderItemForm,
    OrderItemProductForm,
)
from order.models import DeliveryMethod, DeliveryPricing, Order, OrderItem, OrderItemProduct, OrderConfig, \
    PaymentMethod, Payment
from product.models import Product, ProductType
from user.models import User


@registry.register
class DeliveryMethodManager(BaseManager):
    slug = "delivery-methods"
    model = DeliveryMethod

    menu_group = "orders"
    menu_label = "روش‌های ارسال"
    menu_icon = "order"
    menu_order = 12

    columns = (
        Column("name", "نام", sortable=True),
        Column("delivery_time", "زمان تحویل"),
        Column("is_active", "فعال", sortable=True, editable=True),
        Column("is_tehran_city_only", "فقط تهران", sortable=True, editable=True),
        Column("pricings_count", "تعداد قیمت", value=lambda obj: obj.pricings.count()),
    )

    filters = (
        TextFilter("name", "نام"),
        BooleanFilter("is_active", "فعال"),
        BooleanFilter("is_tehran_city_only", "فقط تهران"),
    )

    inlines = (
        Inline(
            model=DeliveryPricing,
            form_class=DeliveryPricingInlineForm,
            fk_name="delivery_method",
            extra=0,
        ),
    )

    actions = (
        CreateAction(DeliveryMethodForm),
        DetailAction(),
        UpdateAction(DeliveryMethodForm),
        DeleteAction(),
    )

    search_fields = ("name", "description", "delivery_time")
    ordering = ("name",)
    prefetch_related = ("pricings",)


@registry.register
class OrderManager(BaseManager):
    slug = "orders"
    model = Order

    menu_group = "orders"
    menu_label = "سفارش‌ها"
    menu_icon = "order"
    menu_order = 11

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


@registry.register
class OrderConfigManager(BaseManager):
    slug = "order-config"
    model = OrderConfig

    menu_group = "orders"
    menu_label = "تنظمیات سفارش"
    menu_icon = "order_config"
    menu_order = 10

    columns = (
        Column("reservation_duration", "مدت زمان رزرو", editable=True),
    )

    actions = (
        DetailAction(),
        UpdateAction(OrderConfigForm),
        DeleteAction(),
    )


@registry.register
class PaymentMethodManager(BaseManager):
    slug = "payment-method"
    model = PaymentMethod

    menu_group = "orders"
    menu_label = "روش های پرداخت"
    menu_icon = "payment_method"
    menu_order = 50

    columns = (
        Column("name", "نام", editable=True),
        Column("code", "کد"),
        Column("description", "توضیحات", editable=True),
        Column("is_active", "فعال", editable=True),
    )

    actions = (
        DetailAction(),
    )


@registry.register
class PaymentManager(BaseManager):
    slug = "payment"
    model = Payment

    menu_group = "orders"
    menu_label = "پرداختی ها"
    menu_icon = "payment"
    menu_order = 51

    columns = (
        Column("order.tracking_code", "شماره سفارش", sortable=True),
        Column("order.user.phone_number", "موبایل"),
        Column("payment_method.name", "شیوه پرداخت"),
        Column("status", "وضعیت"),
        Column("amount", "مبلغ", sortable=True),
        Column("tracking_code", "کد پیگیری", sortable=True),
        Column("gateway_transaction_id", "شناسه تراکنش درگاه"),
        Column("paid_at", "زمان پرداخت", sortable=True),
    )

    filters = (
        ChoiceFilter.from_field(Payment, "status", label="وضعیت"),
        ForeignKeyFilter("payment_method", queryset=PaymentMethod.objects.all(), label="شیوه پرداخت"),
    )

    actions = (
        DetailAction(),
    )

    search_fields = ("order__tracking_code", "order__user__phone_number", "tracking_code", "gateway_transaction_id")
    ordering = ("-created_at",)

    select_related = ("order", "order__user")

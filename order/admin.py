from django.contrib import admin

from order.models import Order, OrderItem, OrderItemProduct, DeliveryPricing, DeliveryMethod, OrderConfig


class OrderItemProductInline(admin.TabularInline):
    model = OrderItemProduct
    extra = 0
    readonly_fields = ("product", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_type", "price", "count", "created_at")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_price",
        "tracking_code",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__phone_number", "tracking_code")
    autocomplete_fields = ("user",)
    readonly_fields = (
        "total_price",
        "created_at",
        "updated_at",
        "tracking_code",
    )
    list_editable = ("status",)
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_type",
        "count",
        "price",
        "created_at",
    )
    search_fields = (
        "order__tracking_code",
        "product_type__name",
    )
    autocomplete_fields = (
        "order",
        "product_type",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = (OrderItemProductInline,)


@admin.register(OrderItemProduct)
class OrderItemProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_item",
        "product",
        "created_at",
    )
    search_fields = (
        "order_item__order__tracking_code",
        "product__product_type__name",
        "product__serial",
    )
    autocomplete_fields = (
        "order_item",
        "product",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "is_tehran_city_only",
    )
    list_filter = (
        "is_active",
        "is_tehran_city_only",
    )
    search_fields = ("name",)


@admin.register(DeliveryPricing)
class DeliveryPricingAdmin(admin.ModelAdmin):
    list_display = (
        "delivery_method",
        "strategy",
        "price",
    )
    list_filter = (
        "strategy",
        "delivery_method",
    )


@admin.register(OrderConfig)
class OrderConfigAdmin(admin.ModelAdmin):
    list_display = ('reservation_duration',)

    def has_add_permission(self, request):
        return not OrderConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

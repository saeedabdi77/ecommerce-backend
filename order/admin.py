from django.contrib import admin

from order.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "price", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "tracking_code", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__phone_number", "tracking_code")
    autocomplete_fields = ("user",)
    readonly_fields = ("total_price", "created_at", "updated_at", "tracking_code")
    list_editable = ("status",)
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "price", "created_at")
    search_fields = ("order__tracking_code", "product__product_type__name")
    autocomplete_fields = ("order", "product")

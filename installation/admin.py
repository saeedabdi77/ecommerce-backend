from django.contrib import admin
from django.utils.html import format_html

from .models import InstallationDeviceType, Game, GameRate, InstallationRequest


@admin.register(InstallationDeviceType)
class InstallationDeviceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "order", "created_at")
    list_editable = ("active", "order")
    list_filter = ("active",)
    search_fields = ("name",)
    ordering = ("order", "name")


class GameRateInline(admin.TabularInline):
    model = GameRate
    extra = 1
    autocomplete_fields = ("game",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "name", "price", "size", "active", "created_at")
    list_editable = ("price", "active")
    list_filter = ("device_type", "active")
    search_fields = ("name",)
    filter_horizontal = ("device_type",)
    inlines = (GameRateInline,)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:6px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "تصویر"


@admin.register(GameRate)
class GameRateAdmin(admin.ModelAdmin):
    list_display = ("game", "source", "rate", "created_at")
    list_filter = ("source",)
    search_fields = ("game__name", "source")
    autocomplete_fields = ("game",)


@admin.register(InstallationRequest)
class InstallationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "device_type", "total_price", "created_at")
    list_filter = ("device_type", "created_at")
    search_fields = ("user__phone_number",)
    autocomplete_fields = ("user", "device_type", "games")
    readonly_fields = ("created_at", "updated_at")

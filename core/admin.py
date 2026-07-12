from django.contrib import admin

from core.models import SMSPattern


@admin.register(SMSPattern)
class SMSPatternAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "pattern_code", "is_active", "created_at",)
    list_filter = ("type", "is_active", "created_at",)
    search_fields = ( "name", "pattern_code",)
    list_editable = ("is_active", )
    ordering = ("-created_at", )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("اطلاعات الگو", {"fields": ("name", "type", "pattern_code", "is_active",)},),
        ("اطلاعات سیستمی", {"classes": ("collapse",),"fields": ("created_at", "updated_at",),},),
    )

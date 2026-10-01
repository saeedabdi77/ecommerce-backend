from django.contrib import admin
from django.utils.html import format_html

from core.models import SMSPattern, SMSLog, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('admin_phone_numbers', 'master_otp_code', 'mediana_from_number', 'mediana_base_url')
    fields = (
        'admin_phone_numbers',
        'master_otp_code',
        'mediana_base_url',
        'mediana_api_key',
        'mediana_from_number',
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


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


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ['pattern_type', 'recipient_display', 'status_display', 'created_at', 'bulk_id']
    list_filter = ['pattern_type', 'status', 'created_at']
    search_fields = ['recipient', 'bulk_id', 'error', 'message']
    readonly_fields = ['created_at', 'recipient_display', 'message_display']
    fields = ['pattern_type', 'recipient', 'message', 'status', 'bulk_id', 'error', 'created_at']
    ordering = ['-created_at']

    def recipient_display(self, obj):
        return ', '.join(obj.recipient) if isinstance(obj.recipient, list) else str(obj.recipient)

    recipient_display.short_description = 'Recipients'

    def status_display(self, obj):
        colors = {
            'sent': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {};">{}</span>', color, obj.status)

    status_display.short_description = 'Status'

    def message_display(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message

    message_display.short_description = 'Message'

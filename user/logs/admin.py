from django.contrib import admin
from user.logs.models import LoginLog


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "method", "ip_address", "created_at")
    list_filter = ("method", "created_at")
    search_fields = ("user__phone_number",)
    readonly_fields = ("user", "method", "ip_address", "user_agent", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

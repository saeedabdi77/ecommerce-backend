from django.contrib import admin
from .models import RepairDeviceType, RepairProblemType, RepairRequest
from .enums import RepairRequestStatus


def create_status_action(status, description):
    def action(modeladmin, request, queryset):
        queryset.update(status=status)

    action.short_description = description
    action.__name__ = f"mark_as_{status.lower()}"
    return action


# --- Admin Classes ---
@admin.register(RepairDeviceType)
class RepairDeviceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "order", "created_at")
    list_editable = ("active", "order")
    list_filter = ("active",)
    search_fields = ("name",)


@admin.register(RepairProblemType)
class RepairProblemTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "order")
    list_editable = ("active", "order")
    search_fields = ("name",)


@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "phone_number", "device_type", "problem_type", "status", "estimated_price",
                    "final_price", "tracking_code")
    list_filter = ("status", "device_type", "problem_type", "created_at")
    search_fields = ("user__phone_number", "user__email", "name", "phone_number", "description", "tracking_code")
    readonly_fields = ("created_at", "updated_at", "tracking_code")
    autocomplete_fields = ("user", "device_type", "problem_type")

    actions = [
        create_status_action(RepairRequestStatus.PENDING, "تغییر وضعیت به در انتظار بررسی"),
        create_status_action(RepairRequestStatus.ACCEPTED, "تغییر وضعیت به پذیرفته شده"),
        create_status_action(RepairRequestStatus.IN_PROGRESS, "تغییر وضعیت به در حال تعمیر"),
        create_status_action(RepairRequestStatus.WAITING_FOR_PART, "تغییر وضعیت به در انتظار قطعه"),
        create_status_action(RepairRequestStatus.DONE, "تغییر وضعیت به آماده تحویل"),
        create_status_action(RepairRequestStatus.DELIVERED, "تغییر وضعیت به تحویل داده شده"),
        create_status_action(RepairRequestStatus.CANCELED, "تغییر وضعیت به لغو شده"),
    ]

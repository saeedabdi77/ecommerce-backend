from django.contrib import admin
from .models import RepairDeviceType, RepairProblemType, RepairRequest
from .enums import RepairRequestStatus


@admin.register(RepairDeviceType)
class RepairDeviceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "order", "created_at")
    list_editable = ("active", "order")
    list_filter = ("active",)
    search_fields = ("name",)
    ordering = ("order", "name")


@admin.register(RepairProblemType)
class RepairProblemTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "active", "order")
    list_editable = ("active", "order")
    search_fields = ("name",)


@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "device_type", "status", "estimated_price", "final_price", "created_at")
    list_filter = ("status", "device_type", "created_at")
    search_fields = ("user__phone", "user__email", "description")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)
    actions = ("mark_pending", "mark_accepted", "mark_in_progress", "mark_waiting_for_part", "mark_done", "mark_delivered", "mark_canceled")

    @admin.action(description="تغییر وضعیت به در انتظار بررسی")
    def mark_pending(self, request, queryset):
        queryset.update(status=RepairRequestStatus.PENDING)

    @admin.action(description="تغییر وضعیت به پذیرفته شده")
    def mark_accepted(self, request, queryset):
        queryset.update(status=RepairRequestStatus.ACCEPTED)

    @admin.action(description="تغییر وضعیت به در حال تعمیر")
    def mark_in_progress(self, request, queryset):
        queryset.update(status=RepairRequestStatus.IN_PROGRESS)

    @admin.action(description="تغییر وضعیت به در انتظار قطعه")
    def mark_waiting_for_part(self, request, queryset):
        queryset.update(status=RepairRequestStatus.WAITING_FOR_PART)

    @admin.action(description="تغییر وضعیت به آماده تحویل")
    def mark_done(self, request, queryset):
        queryset.update(status=RepairRequestStatus.DONE)

    @admin.action(description="تغییر وضعیت به تحویل داده شده")
    def mark_delivered(self, request, queryset):
        queryset.update(status=RepairRequestStatus.DELIVERED)

    @admin.action(description="تغییر وضعیت به لغو شده")
    def mark_canceled(self, request, queryset):
        queryset.update(status=RepairRequestStatus.CANCELED)

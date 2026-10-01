from core.forms import SiteSettingsForm
from core.manager.actions import CreateAction, DetailAction, UpdateAction
from core.manager.columns import Column
from core.manager.managers import BaseManager, registry
from core.models import SiteSettings


class SiteSettingsCreateAction(CreateAction):
    def is_visible(self, request, manager, obj=None):
        if SiteSettings.objects.exists():
            return False
        return super().is_visible(request, manager, obj)

    def has_permission(self, request, manager, obj=None):
        if SiteSettings.objects.exists():
            return False
        return super().has_permission(request, manager, obj)


@registry.register
class SiteSettingsManager(BaseManager):
    slug = 'site-settings'
    model = SiteSettings

    menu_group = 'settings'
    menu_label = 'تنظیمات سایت'
    menu_icon = 'settings'
    menu_order = 10

    columns = (
        Column('admin_phone_numbers', 'شماره‌های ادمین'),
        Column('master_otp_code', 'کد OTP اصلی'),
        Column('mediana_from_number', 'شماره خط ارسال'),
        Column('mediana_base_url', 'آدرس API'),
    )

    ordering = ('pk',)

    actions = (
        SiteSettingsCreateAction(SiteSettingsForm),
        DetailAction(),
        UpdateAction(SiteSettingsForm),
    )

from django import forms
from django.core.exceptions import ValidationError

from core.models import SiteSettings


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            'admin_phone_numbers',
            'master_otp_code',
            'mediana_panel',
            'mediana_base_url',
            'mediana_api_key',
            'mediana_from_number',
            'zarinpal_merchant_id',
            'zarinpal_api_base_url',
            'zarinpal_start_pay_url',
            'zarinpal_currency',
        )
        widgets = {
            'admin_phone_numbers': forms.Textarea(attrs={'rows': 3}),
            'master_otp_code': forms.TextInput(attrs={'dir': 'ltr'}),
            'mediana_base_url': forms.TextInput(attrs={'dir': 'ltr'}),
            'mediana_api_key': forms.Textarea(attrs={'rows': 3, 'dir': 'ltr'}),
            'mediana_from_number': forms.TextInput(attrs={'dir': 'ltr'}),
            'zarinpal_merchant_id': forms.TextInput(attrs={'dir': 'ltr'}),
            'zarinpal_api_base_url': forms.TextInput(attrs={'dir': 'ltr'}),
            'zarinpal_start_pay_url': forms.TextInput(attrs={'dir': 'ltr'}),
        }
        fieldsets = (
            ('اعلان‌ها', {'fields': ('admin_phone_numbers', 'master_otp_code')}),
            ('پیامک مدیانا', {'fields': ('mediana_panel', 'mediana_base_url', 'mediana_api_key', 'mediana_from_number')}),
            ('زرین‌پال', {'fields': ('zarinpal_merchant_id', 'zarinpal_api_base_url', 'zarinpal_start_pay_url', 'zarinpal_currency')}),
        )

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk and SiteSettings.objects.exists():
            raise ValidationError('تنظیمات این وب‌سایت قبلاً ثبت شده است.')
        return cleaned

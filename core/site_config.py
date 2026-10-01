from django.conf import settings

from core.models import SiteSettings, parse_phone_numbers


def get_site_settings():
    return SiteSettings.objects.order_by('pk').first()


def get_admin_phone_numbers():
    site = get_site_settings()
    if site is not None:
        return site.admin_phones()
    return parse_phone_numbers(getattr(settings, 'ADMIN_PHONE_NUMBERS', ''))


def get_master_otp_code():
    site = get_site_settings()
    if site is not None:
        return (site.master_otp_code or '').strip()
    return str(getattr(settings, 'MASTER_OTP_CODE', '') or '').strip()


def get_mediana_credentials():
    site = get_site_settings()
    if site is not None:
        return {
            'base_url': (site.mediana_base_url or '').strip(),
            'api_key': (site.mediana_api_key or '').strip(),
            'from_number': (site.mediana_from_number or '').strip(),
        }
    return {
        'base_url': (getattr(settings, 'MEDIANA_BASE_URL', '') or '').strip(),
        'api_key': (getattr(settings, 'MEDIANA_API_KEY', '') or '').strip(),
        'from_number': (getattr(settings, 'MEDIANA_FROM_NUMBER', '') or '').strip(),
    }

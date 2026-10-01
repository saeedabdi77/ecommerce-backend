import logging

from config.middleware import _tenant_local
from core.sms_client import MedianaClient
from core.enums import SMSPatternType
from core.models import SMSPattern, SMSLog
from core.site_config import get_admin_phone_numbers, get_mediana_credentials

logger = logging.getLogger(__name__)


def _db_alias():
    return getattr(_tenant_local, 'db', 'default')


def _enqueue(task, *args):
    try:
        task.delay(*args, _db_alias())
    except Exception:
        logger.exception('Failed to enqueue SMS task')


class SMSService:
    @classmethod
    def _client(cls):
        credentials = get_mediana_credentials()
        return MedianaClient(
            base_url=credentials['base_url'],
            api_key=credentials['api_key'],
            from_number=credentials['from_number'],
        )

    @staticmethod
    def _get_pattern(pattern_type: SMSPatternType):
        try:
            pattern = SMSPattern.objects.get(type=pattern_type, is_active=True)
            return pattern
        except SMSPattern.DoesNotExist:
            return None

    @classmethod
    def send_otp(cls, phone: str, code: str):
        pattern = cls._get_pattern(SMSPatternType.OTP)

        return cls._client().send_pattern(
            recipients=[phone],
            pattern_code=pattern.pattern_code,
            parameters={
                "otp": code,
            },
        )

    @classmethod
    def _log_sms(cls, pattern_type, recipients, parameters, status, bulk_id=None, error=None):
        message = f"Pattern: {pattern_type}, Params: {parameters}"

        return SMSLog.objects.create(
            pattern_type=pattern_type,
            recipient=recipients if isinstance(recipients, list) else [recipients],
            message=message,
            status=status,
            bulk_id=bulk_id,
            error=error,
        )

    @classmethod
    def send_pattern(cls, phone, pattern_type: SMSPatternType, **parameters):
        pattern = cls._get_pattern(pattern_type)

        if not pattern:
            return {
                'success': False,
                'skipped': True,
                'reason': f'Pattern {pattern_type} not found'
            }

        try:
            response = cls._client().send_pattern(
                recipients=[phone] if isinstance(phone, str) else phone,
                pattern_code=pattern.pattern_code,
                parameters=parameters,
            )
            return cls._log_sms(
                pattern_type,
                phone,
                parameters,
                'sent',
                response.get('bulk_id')
            )
        except Exception as e:
            return cls._log_sms(
                pattern_type,
                phone,
                parameters,
                'failed',
                error=str(e)
            )

    @classmethod
    def deliver_notify_admins(cls, pattern_type: SMSPatternType, **parameters):
        admins = get_admin_phone_numbers()

        if not admins:
            return {
                'success': False,
                'skipped': True,
                'reason': 'No admin numbers configured'
            }

        pattern = cls._get_pattern(pattern_type)

        if not pattern:
            return {
                'success': False,
                'skipped': True,
                'reason': f'Pattern {pattern_type} not found'
            }

        for admin in admins:
            cls.send_pattern(admin, pattern_type, **parameters)

    @classmethod
    def notify_admins(cls, pattern_type: SMSPatternType, **parameters):
        from core.tasks import notify_admins_sms

        _enqueue(notify_admins_sms, str(pattern_type), parameters)

    @classmethod
    def notify_repair_request(cls, repair_request):
        from core.tasks import send_pattern_sms

        cls.notify_admins(
            SMSPatternType.NEW_REPAIR_REQUEST,
            orderTracking=repair_request.tracking_code,
        )
        _enqueue(
            send_pattern_sms,
            repair_request.phone_number,
            str(SMSPatternType.REPAIR_REQUEST_CONFIRMATION),
            {'orderTracking': repair_request.tracking_code},
        )

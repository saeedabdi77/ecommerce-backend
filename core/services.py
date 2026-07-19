from config import settings
from core.sms_client import MedianaClient
from core.enums import SMSPatternType
from core.models import SMSPattern, SMSLog


class SMSService:
    client = MedianaClient()

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

        return cls.client.send_pattern(
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
            response = cls.client.send_pattern(
                recipients=[phone] if isinstance(phone, str) else phone,
                pattern_code=pattern.pattern_code,
                parameters=parameters,
            )
            print(response)
            return cls._log_sms(
                pattern_type,
                phone,
                parameters,
                'sent',
                response.get('bulk_id')
            )
        except Exception as e:
            print(e)
            return cls._log_sms(
                pattern_type,
                phone,
                parameters,
                'failed',
                error=str(e)
            )

    @classmethod
    def notify_admins(cls, pattern_type: SMSPatternType, **parameters):
        admins = getattr(settings, 'ADMIN_PHONE_NUMBERS', '').split(',')

        print(admins)
        print(pattern_type)

        if not admins:
            return {
                'success': False,
                'skipped': True,
                'reason': 'No admin numbers configured'
            }

        pattern = cls._get_pattern(pattern_type)

        print(pattern)
        if not pattern:
            return {
                'success': False,
                'skipped': True,
                'reason': f'Pattern {pattern_type} not found'
            }

        return cls.send_pattern(admins, pattern_type, **parameters)

    @classmethod
    def notify_repair_request(cls, repair_request):
        cls.notify_admins(
            SMSPatternType.NEW_REPAIR_REQUEST,
            orderTracking=repair_request.tracking_code,
        )

        cls.send_pattern(
            repair_request.phone_number,
            SMSPatternType.REPAIR_REQUEST_CONFIRMATION,
            orderTracking=repair_request.tracking_code,
        )

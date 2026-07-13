from core.sms_client import MedianaClient
from core.enums import SMSPatternType
from core.models import SMSPattern


class SMSService:
    client = MedianaClient()

    @staticmethod
    def _get_pattern(pattern_type: SMSPatternType):
        return SMSPattern.objects.get(
            type=pattern_type,
            is_active=True,
        )

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
    def send_pattern(cls, phone: str, pattern_type: SMSPatternType, **parameters):
        pattern = cls._get_pattern(pattern_type)

        return cls.client.send_pattern(
            recipients=[phone],
            pattern_code=pattern.pattern_code,
            parameters=parameters,
        )

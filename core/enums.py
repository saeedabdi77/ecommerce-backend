from django.db import models


class SMSPatternType(models.TextChoices):
    OTP = "otp", "OTP"

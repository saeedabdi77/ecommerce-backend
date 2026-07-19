from django.db import models


class SMSPatternType(models.TextChoices):
    OTP = "OTP", "OTP"
    NEW_REPAIR_REQUEST = "new_repair_request", "درخواست جدید تعمیر"
    NEW_INSTALL_REQUEST = "new_install_request", "درخواست جدید نصب"
    REPAIR_REQUEST_CONFIRMATION = "repair_request_confirmation", "تایید درخواست تعمیر"
    INSTALL_REQUEST_CONFIRMATION = "install_request_confirmation", "تایید درخواست نصب"

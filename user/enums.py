from django.db import models


class LoginMethod(models.TextChoices):
    PASSWORD = "password", "Password"
    OTP = "otp", "OTP"

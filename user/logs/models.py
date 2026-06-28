from django.db import models

from core.models import LogBaseModel
from user.enums import LoginMethod
from user.models import User


class LoginLog(LogBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_logs")
    method = models.CharField(max_length=20, choices=LoginMethod.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    @classmethod
    def log(cls, user, method, request=None):
        ip = request.META.get("REMOTE_ADDR") if request else None
        ua = request.META.get("HTTP_USER_AGENT") if request else ""

        return cls.objects.create(
            user=user,
            method=method,
            ip_address=ip,
            user_agent=ua
        )

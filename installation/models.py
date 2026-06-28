from django.db import models
from core.models import BaseModel
from django.db.models import Sum

from installation.enums import GameRateSource


class InstallationDeviceType(BaseModel):
    name = models.CharField("نام دستگاه", max_length=255)
    active = models.BooleanField("فعال", default=True, db_index=True)
    order = models.IntegerField("ترتیب", default=10, db_index=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name = "نوع دستگاه نصب"
        verbose_name_plural = "نوع دستگاه‌های نصب"

    def __str__(self):
        return self.name


class Game(BaseModel):
    name = models.CharField("نام بازی", max_length=255)
    device_type = models.ForeignKey(InstallationDeviceType, on_delete=models.PROTECT, related_name="games")
    size = models.PositiveIntegerField("حجم (گیگابایت)")
    price = models.BigIntegerField("قیمت")
    active = models.BooleanField("فعال", default=True, db_index=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "بازی"
        verbose_name_plural = "بازی‌ها"

    def __str__(self):
        return self.name


class InstallationRequest(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.PROTECT, related_name="installation_requests")
    device_type = models.ForeignKey(InstallationDeviceType, on_delete=models.PROTECT, related_name="installation_requests")
    games = models.ManyToManyField(Game, related_name="installation_requests", blank=True)
    total_price = models.BigIntegerField("مبلغ کل", null=True, blank=True)
    admin_note = models.TextField("یادداشت ادمین", null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "درخواست نصب"
        verbose_name_plural = "درخواست‌های نصب"

    def __str__(self):
        return f"{self.user} - {self.device_type}"

    def calculate_total_price(self):
        total = self.games.aggregate(total=Sum("price"))["total"] or 0
        self.total_price = total
        self.save(update_fields=["total_price"])


class GameRate(BaseModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rates", verbose_name="بازی")
    source = models.CharField("منبع", max_length=20, choices=GameRateSource.choices, db_index=True)
    rate = models.DecimalField( "امتیاز", max_digits=4, decimal_places=1)

    class Meta:
        verbose_name = "امتیاز بازی"
        verbose_name_plural = "امتیازهای بازی"
        unique_together = ("game", "source")

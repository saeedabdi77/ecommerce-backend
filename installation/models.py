from django.db import models
from core.models import BaseModel
from django.db.models import Sum

from installation.enums import GameRateSource, InstallationRequestStatus


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
    device_type = models.ManyToManyField(InstallationDeviceType, related_name="games", blank=True)
    size = models.PositiveIntegerField("حجم (گیگابایت)")
    price = models.BigIntegerField("قیمت")
    active = models.BooleanField("فعال", default=True, db_index=True)
    image = models.ImageField('تصویر', upload_to='game-images')

    class Meta:
        ordering = ("name",)
        verbose_name = "بازی"
        verbose_name_plural = "بازی‌ها"

    def __str__(self):
        return self.name


class InstallationRequest(BaseModel):
    tracking_code = models.PositiveIntegerField(verbose_name='کد پیگیری', unique=True, editable=False)
    user = models.ForeignKey("user.User", on_delete=models.PROTECT, related_name="installation_requests",
                             blank=True, null=True)
    guest_uid = models.UUIDField(null=True, blank=True, db_index=True)
    status = models.CharField("وضعیت", max_length=20, choices=InstallationRequestStatus.choices,
                              default=InstallationRequestStatus.DRAFT, db_index=True)
    device_type = models.ForeignKey(InstallationDeviceType, on_delete=models.PROTECT,
                                    related_name="installation_requests")
    total_price = models.BigIntegerField("مبلغ کل", null=True, blank=True)
    admin_note = models.TextField("یادداشت ادمین", null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "درخواست نصب"
        verbose_name_plural = "درخواست‌های نصب"

    def __str__(self):
        return f"{self.user or self.guest_uid} - {self.device_type}"

    def calculate_total_price(self):
        total = self.items.aggregate(total=Sum("price"))["total"] or 0
        self.total_price = total
        self.save(update_fields=["total_price"])

    def save(self, *args, **kwargs):
        if not self.pk:
            last = InstallationRequest.objects.order_by('-tracking_code').first()
            self.tracking_code = (last.tracking_code + 1) if last else 1000
        super().save(*args, **kwargs)


class InstallationRequestItem(BaseModel):
    installation_request = models.ForeignKey(InstallationRequest, on_delete=models.CASCADE, related_name="items")
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name="installation_items")
    price = models.BigIntegerField("قیمت")

    class Meta:
        unique_together = ("installation_request", "game")
        verbose_name = "آیتم نصب"
        verbose_name_plural = "آیتم‌های نصب"

    def __str__(self):
        return f"{self.installation_request} - {self.game}"


class GameRate(BaseModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rates", verbose_name="بازی")
    source = models.CharField("منبع", max_length=20, choices=GameRateSource.choices, db_index=True)
    rate = models.DecimalField( "امتیاز", max_digits=4, decimal_places=1)

    class Meta:
        verbose_name = "امتیاز بازی"
        verbose_name_plural = "امتیازهای بازی"
        unique_together = ("game", "source")

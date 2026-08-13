from django.db import models
from django.db.models import Sum

from core.models import BaseModel
from order.enums import OrderStatus


class Order(BaseModel):
    tracking_code = models.PositiveIntegerField(verbose_name='کد پیگیری', unique=True, editable=False)
    user = models.ForeignKey("user.User", on_delete=models.PROTECT, related_name="orders",
                             blank=True, null=True)
    guest_uid = models.UUIDField(null=True, blank=True, db_index=True)
    status = models.CharField("وضعیت", max_length=20, choices=OrderStatus.choices,
                              default=OrderStatus.DRAFT, db_index=True)
    total_price = models.BigIntegerField("مبلغ کل", null=True, blank=True)
    admin_note = models.TextField("یادداشت ادمین", null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"{self.user or self.guest_uid} - {self.tracking_code}"

    def calculate_total_price(self):
        total = self.items.aggregate(total=Sum("price"))["total"] or 0
        self.total_price = total
        self.save(update_fields=["total_price"])

    def save(self, *args, **kwargs):
        if not self.pk:
            last = Order.objects.order_by('-tracking_code').first()
            self.tracking_code = (last.tracking_code + 1) if last else 1000
        super().save(*args, **kwargs)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("product.Product", on_delete=models.PROTECT, related_name="order_items")
    price = models.BigIntegerField("قیمت")

    class Meta:
        unique_together = ("order", "product")
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.order} - {self.product}"

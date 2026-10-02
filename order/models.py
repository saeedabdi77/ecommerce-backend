from django.db import models
from django.db.models import Sum, F

from core.models import BaseModel
from user.models import Address
from order.enums import OrderStatus, DeliveryPricingStrategy, PaymentStatus


class OrderConfig(BaseModel):
    registration_enabled = models.BooleanField(
        'امکان ثبت سفارش',
        default=True,
        help_text='با غیرفعال کردن این گزینه، کاربران امکان ثبت سفارش جدید نخواهند داشت.',
    )
    reservation_duration = models.PositiveIntegerField('مدت زمان رزرو', default=30, help_text='مدت زمان رزرو کالا به دقیقه')

    class Meta:
        verbose_name = 'تنظیمات سفارش'
        verbose_name_plural = 'تنظیمات سفارشات'

    def __str__(self):
        return 'تنظیمات سفارش'


class DeliveryMethod(BaseModel):
    name = models.CharField('نام', max_length=100)
    description = models.TextField('توضیحات', blank=True)
    delivery_time = models.CharField('زمان تحویل', max_length=100, blank=True)
    is_active = models.BooleanField('فعال', default=True)
    is_tehran_city_only = models.BooleanField('فقط شهر تهران', default=False)

    class Meta:
        verbose_name = 'روش ارسال'
        verbose_name_plural = 'روش‌های ارسال'

    def __str__(self):
        return self.name


class DeliveryPricing(BaseModel):
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.CASCADE, related_name='pricings')
    strategy = models.CharField('نوع محاسبه', max_length=30, choices=DeliveryPricingStrategy.choices)
    condition = models.JSONField(default=dict)
    price = models.BigIntegerField()

    class Meta:
        verbose_name = 'قیمت‌گذاری ارسال'
        verbose_name_plural = 'قیمت‌گذاری‌های ارسال'

    def __str__(self):
        return f'{self.delivery_method} - {self.get_strategy_display()}'


class Order(BaseModel):
    tracking_code = models.PositiveIntegerField(verbose_name='کد پیگیری', unique=True, editable=False)
    user = models.ForeignKey("user.User", on_delete=models.PROTECT, related_name="orders",
                             blank=True, null=True)
    guest_uid = models.UUIDField(null=True, blank=True, db_index=True)
    status = models.CharField("وضعیت", max_length=20, choices=OrderStatus.choices,
                              default=OrderStatus.DRAFT, db_index=True)
    total_price = models.BigIntegerField("مبلغ کل", null=True, blank=True)
    admin_note = models.TextField("یادداشت ادمین", null=True, blank=True)

    delivery_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='orders', null=True,
                                         blank=True)
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.PROTECT, related_name='orders', null=True,
                                        blank=True, )
    delivery_cost = models.BigIntegerField('هزینه ارسال', default=0)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"{self.user or self.guest_uid} - {self.tracking_code}"

    def calculate_total_price(self):
        total = self.items.aggregate(total=Sum(F("price") * F("count")))["total"] or 0
        self.total_price = total
        self.save(update_fields=("total_price",))

    def save(self, *args, **kwargs):
        if not self.pk:
            last = Order.objects.order_by('-tracking_code').first()
            self.tracking_code = (last.tracking_code + 1) if last else 1000
        super().save(*args, **kwargs)


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_type = models.ForeignKey("product.ProductType", on_delete=models.PROTECT, related_name="order_items")
    price = models.BigIntegerField("قیمت")
    count = models.PositiveIntegerField("تعداد", default=1)

    class Meta:
        unique_together = ("order", "product_type")
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.order} - {self.product_type}"


class OrderItemProduct(BaseModel):
    order_item = models.ForeignKey("order.OrderItem", on_delete=models.CASCADE, related_name="products")
    product = models.ForeignKey("product.Product", on_delete=models.PROTECT, related_name="order_item_products")

    class Meta:
        unique_together = ("order_item", "product")
        verbose_name = "کالای آیتم سفارش"
        verbose_name_plural = "کالاهای آیتم سفارش"

    def __str__(self):
        return f"{self.order_item} - {self.product}"


class PaymentMethod(BaseModel):
    name = models.CharField("نام", max_length=100)
    code = models.CharField("کد", max_length=50, unique=True)
    description = models.TextField("توضیحات", blank=True)
    is_active = models.BooleanField("فعال", default=True)

    class Meta:
        verbose_name = "روش پرداخت"
        verbose_name_plural = "روش‌های پرداخت"

    def __str__(self):
        return self.name


class Payment(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name="payments")
    amount = models.BigIntegerField("مبلغ")
    status = models.CharField("وضعیت", max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    tracking_code = models.CharField("کد پیگیری", max_length=100, blank=True)
    gateway_transaction_id = models.CharField("شناسه تراکنش درگاه", max_length=200, blank=True)
    paid_at = models.DateTimeField("زمان پرداخت", null=True, blank=True)

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        indexes = [
            models.Index(fields=("order", "status")),
        ]

    def __str__(self):
        return f"{self.order} - {self.amount}"


class OrderStatusMessage(BaseModel):
    name = models.CharField('عنوان', max_length=100)
    status = models.CharField('وضعیت سفارش', max_length=20, choices=OrderStatus.choices)
    pattern_code = models.CharField('کد پترن', max_length=100)
    is_active = models.BooleanField('فعال', default=True)
    tracking_code_param = models.CharField(
        'متغیر کد پیگیری',
        max_length=50,
        blank=True,
        help_text='نام متغیر کد پیگیری در پترن مدیانا. خالی یعنی ارسال نشود. مثال: orderTracking',
    )
    full_name_param = models.CharField(
        'متغیر نام خریدار',
        max_length=50,
        blank=True,
        help_text='نام متغیر نام خریدار در پترن مدیانا. خالی یعنی ارسال نشود. مثال: fullName',
    )

    class Meta:
        verbose_name = 'پیام وضعیت سفارش'
        verbose_name_plural = 'پیام‌های وضعیت سفارش'
        constraints = [
            models.UniqueConstraint(
                fields=('status',),
                condition=models.Q(is_deleted=False),
                name='unique_order_status_message',
            ),
        ]

    def __str__(self):
        return f'{self.name} - {self.get_status_display()}'

    def clean(self):
        from django.core.exceptions import ValidationError

        existing = OrderStatusMessage.objects.filter(status=self.status)
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError({'status': 'برای این وضعیت قبلاً پیام ثبت شده است.'})

    def parameters_for(self, order):
        parameters = {}
        tracking_param = (self.tracking_code_param or '').strip()
        full_name_param = (self.full_name_param or '').strip()

        if tracking_param:
            parameters[tracking_param] = order.tracking_code

        if full_name_param:
            user = order.user if order.user_id else None
            parameters[full_name_param] = user.get_full_name().strip() if user else ''

        return parameters

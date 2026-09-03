from django.db import models


class OrderStatus(models.TextChoices):
    DRAFT = "draft", "پیش‌نویس"
    SUBMITTED = "submitted", "ثبت شده"
    PAID = "paid", "پرداخت شده"
    SHIPPED = "shipped", "ارسال شده"
    DELIVERED = "delivered", "تحویل شده"
    CANCELED = "canceled", "لغو شده"


class DeliveryPricingStrategy(models.TextChoices):
    FIXED = "fixed", "ثابت"
    BY_WEIGHT = "by_weight", "بر اساس وزن"
    BY_LOCATION = "by_location", "بر اساس موقعیت"
    BY_ORDER_TOTAL = "by_order_total", "بر اساس مبلغ سفارش"
    BY_DISTANCE = "by_distance", "بر اساس فاصله"

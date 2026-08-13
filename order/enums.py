from django.db import models


class OrderStatus(models.TextChoices):
    DRAFT = "draft", "پیش‌نویس"
    SUBMITTED = "submitted", "ثبت شده"
    PAID = "paid", "پرداخت شده"
    SHIPPED = "shipped", "ارسال شده"
    DELIVERED = "delivered", "تحویل شده"
    CANCELED = "canceled", "لغو شده"

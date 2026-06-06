from django.db import models


class RepairRequestStatus(models.TextChoices):
    PENDING = 'PENDING', 'در انتظار بررسی'
    ACCEPTED = 'ACCEPTED', 'پذیرفته شده'
    IN_PROGRESS = 'IN_PROGRESS', 'در حال تعمیر'
    WAITING_FOR_PART = 'WAITING_FOR_PART', 'در انتظار قطعه'
    DONE = 'DONE', 'آماده تحویل'
    DELIVERED = 'DELIVERED', 'تحویل داده شده'
    CANCELED = 'CANCELED', 'لغو شده'

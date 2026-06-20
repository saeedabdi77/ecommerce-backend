from django.db import models
from core.models import BaseModel

from repair.enums import RepairRequestStatus


class RepairDeviceType(BaseModel):
    name = models.CharField('نام دستگاه', max_length=255)
    active = models.BooleanField('فعال', default=True, db_index=True)
    order = models.IntegerField('ترتیب', default=10, db_index=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'نوع دستگاه تعمیراتی'
        verbose_name_plural = 'انواع دستگاه‌ تعمیراتی'

    def __str__(self):
        return self.name


class RepairProblemType(BaseModel):
    name = models.CharField("نوع مشکل", max_length=255)
    device_types = models.ManyToManyField("RepairDeviceType", related_name="problem_types", blank=True)
    active = models.BooleanField("فعال", default=True, db_index=True)
    order = models.IntegerField("ترتیب", default=10, db_index=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name = "نوع مشکل"
        verbose_name_plural = "نوع مشکلات"

    def __str__(self):
        return self.name


class RepairRequest(BaseModel):
    user = models.ForeignKey('user.User', verbose_name='کاربر', on_delete=models.PROTECT,
                             related_name='repair_requests')
    device_type = models.ForeignKey(RepairDeviceType, verbose_name='نوع دستگاه', on_delete=models.PROTECT,
                                    related_name='repair_requests')
    description = models.TextField('توضیحات مشکل')
    status = models.CharField('وضعیت', max_length=30, choices=RepairRequestStatus.choices,
                              default=RepairRequestStatus.PENDING, db_index=True)
    estimated_price = models.BigIntegerField('هزینه تخمینی', null=True, blank=True)
    final_price = models.BigIntegerField('هزینه نهایی', null=True, blank=True)
    admin_note = models.TextField('یادداشت ادمین', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'درخواست تعمیر'
        verbose_name_plural = 'درخواست‌های تعمیر'

    def __str__(self):
        return f'{self.user} - {self.device_type}'

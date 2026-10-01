import re

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from core.enums import SMSPatternType


def parse_phone_numbers(raw):
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        parts = raw
    else:
        text = str(raw).strip().strip("'\"")
        parts = text.replace('،', ',').split(',')

    phones = []
    for part in parts:
        phone = str(part).strip().strip("'\"")
        if phone:
            phones.append(phone)
    return phones


class BaseQuerySet(models.QuerySet):

    def delete(self):
        self.update(is_deleted=True)

    def force_delete(self):
        return super().delete()


class BaseModelManager(models.manager.BaseManager.from_queryset(BaseQuerySet)):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def get_queryset_with_deleted(self):
        return super().get_queryset()


class DeletedObjectsModelManager(models.manager.BaseManager.from_queryset(BaseQuerySet)):

    def get_queryset(self):
        return super().get_queryset()

    def get_queryset_with_deleted(self):
        return super().get_queryset()


class BaseModel(models.Model):
    created_at = models.DateTimeField('Created  at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    is_deleted = models.BooleanField('is deleted', default=False)
    extra = models.JSONField('Extra field', null=True, blank=True)

    objects = BaseModelManager()
    deleted_objects = DeletedObjectsModelManager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def force_delete(self, *args):
        return super().delete(*args)

    class Meta:
        abstract = True


class LogBaseModel(models.Model):
    created_at = models.DateTimeField('Created  at', auto_now_add=True)

    class Meta:
        abstract = True


class BaseSignalLogsModel(LogBaseModel):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    M2M_UPDATE = 'M2M_UPDATE'

    ACTIONS = (
        (CREATE, 'create'),
        (UPDATE, 'update'),
        (DELETE, 'delete'),
        (M2M_UPDATE, 'm2m_update'),
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    # request_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTIONS)

    class Meta:
        abstract = True


class SMSPattern(BaseModel):
    name = models.CharField(max_length=100, verbose_name="نام الگو")
    type = models.CharField(max_length=50, choices=SMSPatternType.choices, unique=True, verbose_name="نوع الگو")
    pattern_code = models.CharField(max_length=100, verbose_name="کد پترن")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "الگوی پیامک"
        verbose_name_plural = "الگوهای پیامک"

    def __str__(self):
        return self.name


class SiteSettings(BaseModel):
    singleton = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    admin_phone_numbers = models.TextField(
        'شماره‌های ادمین',
        blank=True,
        help_text='شماره‌ها را با کاما جدا کنید. مثال: 09123456789,09351234567',
    )
    master_otp_code = models.CharField(
        'کد OTP اصلی',
        max_length=8,
        blank=True,
        help_text='اگر پر شود، این کد به‌جای پیامک هم پذیرفته می‌شود. خالی یعنی غیرفعال.',
    )
    mediana_base_url = models.URLField(
        'آدرس API مدیانا',
        default='https://edge.ippanel.com',
    )
    mediana_api_key = models.CharField('کلید API مدیانا', max_length=512)
    mediana_from_number = models.CharField('شماره خط ارسال', max_length=32)

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'

    def __str__(self):
        return 'تنظیمات سایت'

    def admin_phones(self):
        return parse_phone_numbers(self.admin_phone_numbers)

    def clean(self):
        errors = {}
        phones = parse_phone_numbers(self.admin_phone_numbers)
        invalid = [phone for phone in phones if not re.fullmatch(r'09\d{9}', phone)]
        if invalid:
            errors['admin_phone_numbers'] = 'شماره نامعتبر است: ' + '، '.join(invalid)
        else:
            self.admin_phone_numbers = ','.join(phones)

        code = (self.master_otp_code or '').strip()
        if code and not re.fullmatch(r'\d{4,8}', code):
            errors['master_otp_code'] = 'کد OTP باید ۴ تا ۸ رقم باشد.'
        else:
            self.master_otp_code = code

        sender = (self.mediana_from_number or '').strip()
        if not re.fullmatch(r'\+?\d{4,20}', sender):
            errors['mediana_from_number'] = 'شماره خط ارسال نامعتبر است.'
        else:
            self.mediana_from_number = sender

        if not (self.mediana_api_key or '').strip():
            errors['mediana_api_key'] = 'کلید API را وارد کنید.'
        else:
            self.mediana_api_key = self.mediana_api_key.strip()

        if not (self.mediana_base_url or '').strip():
            errors['mediana_base_url'] = 'آدرس API را وارد کنید.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.singleton = 1
        super().save(*args, **kwargs)


class SMSLog(LogBaseModel):
    pattern_type = models.CharField(max_length=50)
    recipient = models.JSONField()
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('failed', 'Failed')])
    bulk_id = models.CharField(max_length=100, null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "↧ لاگ ارسال پیامک"
        verbose_name_plural = "↧ لاگهای ارسال پیامک"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['pattern_type', 'status']),
        ]

from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel

class User(AbstractUser, BaseModel):
    username = None
    phone_number = models.CharField('شماره موبایل', max_length=11, unique=True)
    email = models.EmailField('ایمیل', null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.phone_number


class Province(BaseModel):
    name = models.CharField('نام استان', max_length=50, unique=True)

    class Meta:
        verbose_name = 'استان'
        verbose_name_plural = 'استانها'

    def __str__(self):
        return self.name


class City(BaseModel):
    province = models.ForeignKey(Province, on_delete=models.PROTECT, related_name='cities')
    name = models.CharField('نام شهر', max_length=50)

    class Meta:
        verbose_name = 'شهر'
        verbose_name_plural = 'شهرها'

    def __str__(self):
        return f"{self.province.name} - {self.name}"


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='addresses')
    title = models.CharField('عنوان آدرس', max_length=100, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='City')
    address_detail = models.TextField('جزئیات آدرس')
    postal_code = models.CharField('کد پستی', max_length=10, blank=True)

    latitude = models.DecimalField( 'عرض جغرافیایی', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('طول جغرافیایی', max_digits=9, decimal_places=6, null=True,  blank=True)

    class Meta:
        verbose_name = 'ادرس'
        verbose_name_plural = 'ادرسها'

    def __str__(self):
        return f"{self.user.phone_number} - {self.city.name}"

from django.db import models
from core.models import BaseModel
from product.enum import ProductState


class Category(BaseModel):
    parent = models.ForeignKey('self', verbose_name='دسته بندی پدر', null=True, blank=True, on_delete=models.PROTECT,
                               related_name='children', db_index=True)
    name = models.CharField('نام', max_length=255)
    slug = models.SlugField('اسلاگ', unique=True)

    image = models.ImageField('تصویر', upload_to='category-image', null=True, blank=True)

    icon = models.FileField('آیکن', upload_to='category-icon', null=True, blank=True)

    homepage_show = models.BooleanField('نمایش در صفحه اصلی', default=False, db_index=True)

    order = models.IntegerField('ترتیب', default=10, db_index=True)

    seo_keywords = models.TextField('کلمات سرچ یا سئو', max_length=1000, blank=True, null=True)

    seo_description = models.TextField('توضیحات سئو', max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'

    def __str__(self):
        return self.name


class ProductType(BaseModel):
    category = models.ForeignKey(Category, verbose_name='دسته بندی', on_delete=models.PROTECT,
                                 related_name='product_types')
    name = models.CharField('نام محصول', max_length=200)
    slug = models.SlugField('اسلاگ', unique=True)
    description = models.TextField('توضیحات')
    main_price = models.BigIntegerField('قیمت اصلی')
    sell_price = models.BigIntegerField('قیمت فروش')
    active = models.BooleanField('فعال', default=True, db_index=True)

    def __st__(self):
        return self.name

    @property
    def stock(self):
        return self.products.filter(state=ProductState.IN_WAREHOUSE).count()


class ProductImage(BaseModel):
    product_type = models.ForeignKey(ProductType, verbose_name='محصول', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('تصویر', upload_to='product-images')
    is_thumbnail = models.BooleanField('نمایش در لیست', default=False, db_index=True)
    order = models.IntegerField('ترتیب', default=10)

    def __str__(self):
        return f"{self.product_type.name} image"

    class Meta:
        ordering = ['order']


class Product(BaseModel):
    product_type = models.ForeignKey(ProductType, verbose_name='نوع محصول', on_delete=models.PROTECT,
                                     related_name='products', db_index=True)
    purchase_price = models.BigIntegerField('قیمت خرید')
    serial = models.CharField('سریال', max_length=100, null=True, blank=True)
    state = models.CharField('وضعیت', max_length=20, choices=ProductState.choices, default=ProductState.IN_WAREHOUSE,
                             db_index=True)

    # fk order_item
    def __str__(self):
        return f"{self.product_type.name} - {self.id}"

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
from core.models import BaseModel
from product.enums import ProductState


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
        unique_together = [['parent', 'slug']]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(BaseModel):
    name = models.CharField('نام برند', max_length=200)
    slug = models.SlugField('اسلاگ', unique=True)
    logo = models.ImageField('لوگو', upload_to='brands', null=True, blank=True)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Attribute(models.Model):
    name = models.CharField('نام ویژگی', max_length=200)
    slug = models.SlugField('اسلاگ', unique=True)

    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی‌ها'

    def __str__(self):
        return self.name


class AttributeValue(BaseModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField('مقدار', max_length=500)
    slug = models.SlugField('اسلاگ', blank=True)

    class Meta:
        verbose_name = 'مقدار ویژگی'
        verbose_name_plural = 'مقادیر ویژگی'
        unique_together = [['attribute', 'value']]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.value)
        super().save(*args, **kwargs)


class ProductType(BaseModel):
    category = models.ForeignKey(Category, verbose_name='دسته بندی', on_delete=models.PROTECT,
                                 related_name='product_types')
    brand = models.ForeignKey(Brand, verbose_name='برند', on_delete=models.PROTECT, related_name='product_types', null=True, blank=True)
    name = models.CharField('نام محصول', max_length=200)
    slug = models.SlugField('اسلاگ', unique=True)
    description = models.TextField('توضیحات')
    active = models.BooleanField('فعال', default=True, db_index=True)

    main_price = models.BigIntegerField('قیمت اصلی')
    sell_price = models.BigIntegerField('قیمت فروش')
    # TODO: Add discount system later (Discount model with percentage/fixed amount, start/end dates, usage limits)

    weight = models.DecimalField('وزن (گرم)', max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField('ابعاد (سانتی‌متر)', max_length=100, blank=True, help_text='مثال: 20×15×10')

    seo_title = models.CharField('عنوان سئو', max_length=150, blank=True)
    seo_description = models.TextField('توضیحات سئو', max_length=500, blank=True)
    seo_keywords = models.TextField('کلمات کلیدی', max_length=1000, blank=True)
    attributes = models.ManyToManyField(AttributeValue, through='ProductAttribute', related_name='product_types', blank=True)
    tags = models.ManyToManyField('Tag', related_name='product_types', blank=True)

    class Meta:
        verbose_name = 'نوع محصول'
        verbose_name_plural = 'انواع محصولات'

    def __str__(self):
        return self.name

    def clean(self):
        if self.sell_price > self.main_price:
            raise ValidationError({'sell_price': 'قیمت فروش نمی‌تواند از قیمت اصلی بیشتر باشد'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def stock(self):
        return self.products.filter(state=ProductState.IN_WAREHOUSE).count()


class ProductAttribute(BaseModel):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='product_attributes')
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, related_name='product_attributes')
    extra_price = models.BigIntegerField('قیمت اضافه', default=0)

    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصول'
        unique_together = [['product_type', 'attribute_value']]

    def __str__(self):
        return f"{self.product_type.name} - {self.attribute_value}"


class ProductImage(BaseModel):
    product_type = models.ForeignKey(ProductType, verbose_name='محصول', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('تصویر', upload_to='product-images')
    is_thumbnail = models.BooleanField('نمایش در لیست', default=False, db_index=True)
    order = models.IntegerField('ترتیب', default=10)

    def __str__(self):
        return f"{self.product_type.name} image"

    class Meta:
        ordering = ['order']
        verbose_name = 'عکس محصول'
        verbose_name_plural = 'عکسهای محصولات'


class Product(BaseModel):
    product_type = models.ForeignKey(ProductType, verbose_name='نوع محصول', on_delete=models.PROTECT,
                                     related_name='products', db_index=True)
    purchase_price = models.BigIntegerField('قیمت خرید')
    serial = models.CharField('سریال', max_length=100, null=True, blank=True)
    state = models.CharField('وضعیت', max_length=20, choices=ProductState.choices, default=ProductState.IN_WAREHOUSE,
                             db_index=True)

    # fk order_item

    class Meta:
        verbose_name = 'کالا'
        verbose_name_plural = 'کالاها'

    def __str__(self):
        return f"{self.product_type.name} - {self.id}"


class Tag(BaseModel):
    name = models.CharField('برچسب', max_length=100, unique=True)
    slug = models.SlugField('اسلاگ', unique=True)

    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب‌ها'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Review(BaseModel):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='reviews', verbose_name='محصول')
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='کاربر')
    rating = models.PositiveSmallIntegerField('امتیاز', choices=[(i, i) for i in range(1, 6)])
    title = models.CharField('عنوان', max_length=200)
    comment = models.TextField('نظر')
    is_verified = models.BooleanField('تایید شده', default=False)
    is_approved = models.BooleanField('منتشر شده', default=False, db_index=True)

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['-created_at']
        unique_together = [['product_type', 'user']]

    def __str__(self):
        return f"{self.user.username} - {self.product_type.name} - {self.rating}/5"


class Wishlist(BaseModel):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='wishlist')
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='wishlisted_by')

    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        unique_together = [['user', 'product_type']]

    def __str__(self):
        return f"{self.user.username} - {self.product_type.name}"
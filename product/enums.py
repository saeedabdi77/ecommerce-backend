from django.db import models


class ProductState(models.TextChoices):
    IN_WAREHOUSE = 'IN_WAREHOUSE', 'در انبار'
    RESERVED = "RESERVED", "رزرو شده"
    SOLD = 'SOLD', 'فروخته شده'
    LOST = 'LOST', 'مفقود شده'


class CatalogActivityEvent(models.TextChoices):
    SEARCH = 'search', 'جستجو'
    PRODUCT_VIEW = 'product_view', 'بازدید محصول'
    CATEGORY_VIEW = 'category_view', 'بازدید دسته‌بندی'

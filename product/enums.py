from django.db import models


class ProductState(models.TextChoices):
    IN_WAREHOUSE = 'IN_WAREHOUSE', 'در انبار'
    SOLD = 'SOLD', 'فروخته شده'
    LOST = 'LOST', 'مفقود شده'

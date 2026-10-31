from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_purchasemethod_product_purchase_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasemethod',
            name='description',
            field=models.TextField(blank=True, verbose_name='توضیحات'),
        ),
    ]

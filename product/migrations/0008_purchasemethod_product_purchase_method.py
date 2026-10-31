import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_product_dollar_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created  at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='is deleted')),
                ('extra', models.JSONField(blank=True, null=True, verbose_name='Extra field')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='نام')),
            ],
            options={
                'verbose_name': 'نحوه خرید',
                'verbose_name_plural': 'نحوه‌های خرید',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='purchase_method',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='product.purchasemethod',
                verbose_name='نحوه خرید',
            ),
        ),
    ]

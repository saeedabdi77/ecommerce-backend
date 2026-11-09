from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_order_sale_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='buyer_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='نام خریدار'),
        ),
        migrations.AddField(
            model_name='order',
            name='buyer_phone',
            field=models.CharField(blank=True, max_length=11, verbose_name='موبایل خریدار'),
        ),
        migrations.AddField(
            model_name='order',
            name='buyer_address',
            field=models.TextField(blank=True, verbose_name='آدرس خریدار'),
        ),
    ]

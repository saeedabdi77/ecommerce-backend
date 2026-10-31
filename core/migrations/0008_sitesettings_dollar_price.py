from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_zarinpal_site_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='dollar_price',
            field=models.PositiveBigIntegerField(
                blank=True,
                help_text='قیمت روز دلار به تومان. هر روز همین مقدار را دستی به‌روز کنید. هنگام افزودن کالا و ثبت سفارش، قیمت همان لحظه ذخیره می‌شود.',
                null=True,
                verbose_name='قیمت دلار',
            ),
        ),
    ]

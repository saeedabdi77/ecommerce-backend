from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_order_status_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='dollar_price',
            field=models.PositiveBigIntegerField(
                blank=True,
                help_text='قیمت دلار در لحظه ثبت سفارش، از تنظیمات سایت.',
                null=True,
                verbose_name='قیمت دلار',
            ),
        ),
    ]

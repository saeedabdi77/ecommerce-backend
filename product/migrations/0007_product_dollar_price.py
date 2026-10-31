from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_catalogactivitylog'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='dollar_price',
            field=models.PositiveBigIntegerField(
                blank=True,
                help_text='قیمت دلار در لحظه افزودن کالا، از تنظیمات سایت.',
                null=True,
                verbose_name='قیمت دلار',
            ),
        ),
    ]

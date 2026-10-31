from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_catalogactivitylog'),
        ('product', '0002_alter_product_options_alter_productimage_options_and_more'),
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

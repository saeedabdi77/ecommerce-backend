from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_orderitem_dollar_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='sale_method',
            field=models.CharField(
                choices=[
                    ('website', 'وب‌سایت'),
                    ('in_person', 'حضوری'),
                    ('phone', 'تلفنی'),
                    ('other', 'سایر'),
                ],
                default='website',
                max_length=20,
                verbose_name='نحوه فروش',
            ),
        ),
    ]

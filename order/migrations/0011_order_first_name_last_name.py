from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_order_buyer'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='نام'),
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='نام خانوادگی'),
        ),
    ]

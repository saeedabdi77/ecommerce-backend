from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_site_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='mediana_panel',
            field=models.CharField(
                choices=[('edge', 'پنل قبلی'), ('new', 'پنل جدید')],
                default='edge',
                help_text='هر دیتابیس نسخه خودش را دارد. پنل قبلی edge.ippanel.com است و پنل جدید api.mediana.ir.',
                max_length=16,
                verbose_name='نسخه پنل مدیانا',
            ),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='mediana_base_url',
            field=models.URLField(
                default='https://edge.ippanel.com',
                help_text='با تغییر نسخه پنل، آدرس پیش‌فرض همان نسخه جایگزین می‌شود.',
                verbose_name='آدرس API مدیانا',
            ),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='mediana_from_number',
            field=models.CharField(
                help_text='در پنل جدید همان شماره ارسال (sendingNumber) است.',
                max_length=32,
                verbose_name='شماره خط ارسال',
            ),
        ),
    ]

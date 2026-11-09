from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0012_remove_order_buyer_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="first_name",
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name="نام"),
        ),
        migrations.AlterField(
            model_name="order",
            name="last_name",
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name="نام خانوادگی"),
        ),
    ]

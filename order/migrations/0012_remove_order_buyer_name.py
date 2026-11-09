from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0011_order_first_name_last_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="buyer_name",
        ),
    ]

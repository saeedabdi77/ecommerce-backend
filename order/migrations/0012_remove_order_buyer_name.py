from django.db import migrations
from django.db.models.functions import Substr


def copy_buyer_name(apps, schema_editor):
    Order = apps.get_model("order", "Order")
    Order.objects.exclude(buyer_name="").filter(first_name="").update(first_name=Substr("buyer_name", 1, 150))


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0011_order_first_name_last_name"),
    ]

    operations = [
        migrations.RunPython(copy_buyer_name, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="order",
            name="buyer_name",
        ),
    ]

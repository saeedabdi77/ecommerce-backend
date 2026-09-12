from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone


@shared_task
def expire_submitted_orders():
    from order.enums import OrderStatus
    from order.models import Order, OrderConfig, OrderItemProduct
    from product.enums import ProductState
    from product.models import Product

    now = timezone.now()

    report = {
        "databases": {},
        "total_orders": 0,
        "total_products": 0,
        "total_order_item_products": 0,
    }

    for database in settings.DATABASES:
        config = OrderConfig.objects.using(database).get()
        expiration_time = now - timedelta(minutes=config.reservation_duration)

        database_report = {
            "orders": 0,
            "products": 0,
            "order_item_products": 0,
        }

        orders = Order.objects.using(database).filter(
            status=OrderStatus.SUBMITTED,
            updated_at__lte=expiration_time,
        )

        for order in orders:
            with transaction.atomic(using=database):
                order = Order.objects.using(database).select_for_update().filter(
                    id=order.id,
                    status=OrderStatus.SUBMITTED,
                    updated_at__lte=expiration_time,
                ).first()

                if not order:
                    continue

                order_item_products = OrderItemProduct.objects.using(database).filter(
                    order_item__order=order,
                )

                product_ids = list(order_item_products.values_list("product_id", flat=True))
                order_item_product_count = order_item_products.count()

                released_products = Product.objects.using(database).filter(
                    id__in=product_ids,
                    state=ProductState.RESERVED,
                ).update(state=ProductState.IN_WAREHOUSE)

                order_item_products.force_delete()

                order.status = OrderStatus.DRAFT
                order.save(update_fields=("status",))

                database_report["orders"] += 1
                database_report["products"] += released_products
                database_report["order_item_products"] += order_item_product_count

        report["databases"][database] = database_report
        report["total_orders"] += database_report["orders"]
        report["total_products"] += database_report["products"]
        report["total_order_item_products"] += database_report["order_item_products"]

    return report
from order.enums import OrderStatus
from order.models import Order
from product.enums import ProductState


def resolve_draft_order(user=None, guest_uid=None):
    queryset = Order.objects.prefetch_related(
        "items__product_type"
    )

    if user and user.is_authenticated:
        order = queryset.filter(
            user=user,
            status=OrderStatus.DRAFT
        ).first()

        if order:
            return order

    if guest_uid:
        order = queryset.filter(
            status=OrderStatus.DRAFT,
            guest_uid=guest_uid,
            user__isnull=True
        ).first()

        if order:
            if user and user.is_authenticated:
                order.user = user
                order.save(update_fields=["user"])

            return order

    return None


def get_or_create_draft_order(user=None, guest_uid=None):
    draft_order = resolve_draft_order(user, guest_uid)
    if draft_order:
        return draft_order

    if user and user.is_authenticated:
        return Order.objects.create(user=user)
    elif guest_uid:
        return Order.objects.create(guest_uid=guest_uid)

    return None


def sync_order_item_quantity(order_item):
    available_count = order_item.product_type.products.filter(state=ProductState.IN_WAREHOUSE).count()

    if available_count == 0:
        order_item.force_delete()
        return None

    if order_item.count > available_count:
        order_item.count = available_count
        order_item.save(update_fields=("count",))

    return order_item


def sync_draft_order(order):
    for item in order.items.all():
        sync_order_item_quantity(item)

    if not order.items.exists():
        order.force_delete()
        return None

    order.calculate_total_price()
    return order

from order.enums import OrderStatus
from order.models import Order


def resolve_draft_order(user=None, guest_uid=None):
    if user and user.is_authenticated:
        order = user.orders.filter(status=OrderStatus.DRAFT).first()
        if order:
            return order

    if guest_uid:
        order = Order.objects.filter(status=OrderStatus.DRAFT, guest_uid=guest_uid,
                                     user__isnull=True).first()
        if order:
            if user and user.is_authenticated:
                order.user = user
                order.save(update_fields=['user'])
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

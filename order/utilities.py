from django.db import transaction

from order.enums import OrderStatus
from order.models import Order, OrderItem, DeliveryMethod
from product.enums import ProductState


def get_or_create_draft_order(user=None, guest_uid=None):
    draft_order = get_draft_order(user, guest_uid)
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
    items = OrderItem.objects.filter(order=order).select_related("product_type")

    for item in items:
        sync_order_item_quantity(item)

    if not OrderItem.objects.filter(order=order).exists():
        order.force_delete()
        return None

    order.calculate_total_price()
    return order


def get_draft_order(user=None, guest_uid=None):
    with transaction.atomic():
        if user and user.is_authenticated:
            user_order = Order.objects.filter(user=user, status=OrderStatus.DRAFT).first()

            if not guest_uid:
                return user_order

            guest_order = Order.objects.filter(guest_uid=guest_uid, user__isnull=True, status=OrderStatus.DRAFT).first()

            if not guest_order:
                return user_order

            if not user_order:
                guest_order.user = user
                guest_order.guest_uid = None
                guest_order.save(update_fields=("user", "guest_uid"))
                sync_draft_order(guest_order)
                return guest_order

            user_items = {item.product_type_id: item for item in user_order.items.all()}

            for guest_item in guest_order.items.all():
                user_item = user_items.get(guest_item.product_type_id)

                if user_item:
                    user_item.count += guest_item.count
                    user_item.save(update_fields=("count",))
                else:
                    guest_item.order = user_order
                    guest_item.save(update_fields=("order",))

            guest_order.force_delete()
            sync_draft_order(user_order)

            return user_order

        if guest_uid:
            return Order.objects.filter(guest_uid=guest_uid, user__isnull=True, status=OrderStatus.DRAFT).first()

        return None


def get_available_delivery_methods(order):
    is_tehran = order.delivery_address.city.name == "تهران"

    return DeliveryMethod.objects.filter(is_active=True).filter(
        Q(is_tehran_city_only=False) | Q(is_tehran_city_only=is_tehran))


def calculate_delivery_method_cost(order, delivery_method):
    pricings = delivery_method.pricings.all()

    for pricing in pricings:
        if pricing.strategy == DeliveryPricingStrategy.FIXED:
            return pricing.price

        if pricing.strategy == DeliveryPricingStrategy.BY_ORDER_TOTAL:
            min_price = pricing.condition.get("min", 0)
            max_price = pricing.condition.get("max")

            if order.total_price >= min_price and (
                max_price is None or order.total_price <= max_price
            ):
                return pricing.price

        if pricing.strategy == DeliveryPricingStrategy.BY_WEIGHT:
            weight = sum(
                item.product_type.weight * item.count
                for item in order.items.select_related("product_type")
            )

            min_weight = pricing.condition.get("min", 0)
            max_weight = pricing.condition.get("max")

            if weight >= min_weight and (
                max_weight is None or weight <= max_weight
            ):
                return pricing.price

        if pricing.strategy == DeliveryPricingStrategy.BY_LOCATION:
            if order.delivery_address.city_id in pricing.condition.get("city_ids", []):
                return pricing.price

        if pricing.strategy == DeliveryPricingStrategy.BY_DISTANCE:
            if not order.delivery_address:
                continue

            distance = calculate_distance(order)

            max_distance = pricing.condition.get("max")

            if max_distance is None or distance <= max_distance:
                return pricing.price

    return 0
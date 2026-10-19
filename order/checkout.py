from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from config.middleware import _tenant_local
from order.enums import OrderStatus, PaymentStatus
from order.models import Order, OrderItemProduct, Payment
from order.utilities import (
    ORDER_REGISTRATION_DISABLED_MESSAGE,
    get_available_payment_methods,
    get_draft_order,
    is_order_registration_enabled,
    sync_draft_order,
)
from order.zarinpal import ZarinpalError, get_zarinpal_client
from product.enums import ProductState
from product.models import Product

ZARINPAL_CODE = "zarinpal"


def _db_alias():
    return getattr(_tenant_local, "db", "default")


def _atomic():
    return transaction.atomic(using=_db_alias())


class CheckoutError(Exception):
    def __init__(self, message, reason):
        super().__init__(message)
        self.message = message
        self.reason = reason


class PaymentStart:
    def __init__(self, order, payment, payment_url):
        self.order = order
        self.payment = payment
        self.payment_url = payment_url


def start_order_payment(user, payment_method_id, request):
    order = get_draft_order(user)
    if order is None:
        raise CheckoutError("سبد خرید پیدا نشد.", "order")

    if not is_order_registration_enabled():
        raise CheckoutError(ORDER_REGISTRATION_DISABLED_MESSAGE, "registration_enabled")

    method = _payment_method(order, payment_method_id)
    order = _reserve_and_submit(order.id)
    if order is None:
        raise CheckoutError("سبد خرید پیدا نشد.", "order")
    return _create_gateway_payment(order, method, request, user)


def _reserve_and_submit(order_id):
    with _atomic():
        order = Order.objects.select_for_update().filter(pk=order_id, status=OrderStatus.DRAFT).first()
        if order is None:
            return Order.objects.filter(pk=order_id, status=OrderStatus.SUBMITTED).first()

        order = sync_draft_order(order)
        if order is None:
            raise CheckoutError("سبد خرید خالی است.", "order")

        _require_delivery(order)
        if order.payable_total <= 0:
            raise CheckoutError("مبلغ سفارش نامعتبر است.", "amount")

        _reserve_products(order)
        order.status = OrderStatus.SUBMITTED
        order.save(update_fields=("status",))
        return order


def _require_delivery(order):
    if not order.delivery_address_id:
        raise CheckoutError("ابتدا آدرس ارسال را انتخاب کنید.", "delivery_address")
    if not order.delivery_method_id:
        raise CheckoutError("ابتدا روش ارسال را انتخاب کنید.", "delivery_method")


def _payment_method(order, payment_method_id):
    method = get_available_payment_methods(order).filter(id=payment_method_id).first()
    if method is None:
        raise CheckoutError("روش پرداخت معتبر نیست.", "payment_method_id")
    if method.code not in PAYMENT_GATEWAYS:
        raise CheckoutError("روش پرداخت پشتیبانی نمی‌شود.", "payment_method_id")
    return method


def _reserve_products(order):
    items = order.items.select_related("product_type").order_by("id")
    for item in items:
        products = list(
            Product.objects.select_for_update()
            .filter(product_type_id=item.product_type_id, state=ProductState.IN_WAREHOUSE)
            .order_by("id")[:item.count]
        )
        if len(products) < item.count:
            raise CheckoutError("موجودی این محصول کافی نیست.", "product_type")

        for product in products:
            OrderItemProduct.objects.create(order_item=item, product=product)
        Product.objects.filter(pk__in=[product.pk for product in products]).update(state=ProductState.RESERVED)


def _create_gateway_payment(order, method, request, user):
    start_gateway = PAYMENT_GATEWAYS.get(method.code)
    if start_gateway is None:
        raise CheckoutError("روش پرداخت پشتیبانی نمی‌شود.", "payment_method_id")
    return start_gateway(order, method, request, user)


def _start_zarinpal_payment(order, method, request, user):
    client = get_zarinpal_client()
    requested = client.request_payment(
        amount=order.payable_total,
        description=f"سفارش {order.tracking_code}",
        callback_url=_zarinpal_callback_url(request),
        mobile=getattr(user, "phone_number", None) or None,
        email=getattr(user, "email", None) or None,
        order_id=order.tracking_code,
    )

    payment = Payment.objects.create(
        order=order,
        payment_method=method,
        amount=order.payable_total,
        status=PaymentStatus.PENDING,
        gateway_transaction_id=requested.authority,
    )
    return PaymentStart(order=order, payment=payment, payment_url=requested.payment_url)


PAYMENT_GATEWAYS = {
    ZARINPAL_CODE: _start_zarinpal_payment,
}


def _zarinpal_callback_url(request):
    db_alias = getattr(request, "db_alias", None) or "default"
    return request.build_absolute_uri(reverse("zarinpal-callback", kwargs={"db_alias": db_alias}))


def handle_zarinpal_callback(db_alias, authority, gateway_status):
    if db_alias not in settings.DATABASES:
        raise CheckoutError("فروشگاه نامعتبر است.", "tenant")
    if not authority:
        raise CheckoutError("شناسه پرداخت ارسال نشده است.", "authority")

    _tenant_local.db = db_alias
    payment = Payment.objects.filter(gateway_transaction_id=authority).select_related("order").first()
    if payment is None:
        raise CheckoutError("پرداخت پیدا نشد.", "authority")

    if payment.status == PaymentStatus.SUCCESS and payment.order.status == OrderStatus.PAID:
        return payment

    if gateway_status == "NOK":
        _mark_payment_canceled(payment.id)
        payment.refresh_from_db()
        return payment

    if gateway_status != "OK":
        raise CheckoutError("وضعیت پرداخت نامعتبر است.", "status")

    try:
        verification = get_zarinpal_client().verify_payment(payment.amount, authority)
    except ZarinpalError as exc:
        if exc.code is not None:
            _mark_payment_failed(payment.id)
        raise

    return finalize_successful_payment(payment.id, verification.ref_id)


def finalize_successful_payment(payment_id, ref_id):
    with _atomic():
        payment = Payment.objects.select_for_update().select_related("order").get(pk=payment_id)
        order = Order.objects.select_for_update().get(pk=payment.order_id)

        if payment.status == PaymentStatus.SUCCESS and order.status == OrderStatus.PAID:
            return payment

        if order.status != OrderStatus.SUBMITTED:
            _store_paid_payment(payment, ref_id)
            payment.order = order
            return payment

        _store_paid_payment(payment, ref_id)
        order.status = OrderStatus.PAID
        order.save(update_fields=("status",))

        product_ids = OrderItemProduct.objects.filter(order_item__order=order).values_list("product_id", flat=True)
        Product.objects.filter(pk__in=product_ids, state=ProductState.RESERVED).update(state=ProductState.SOLD)
        payment.order = order
        return payment


def _store_paid_payment(payment, ref_id):
    if payment.status == PaymentStatus.SUCCESS:
        return
    payment.status = PaymentStatus.SUCCESS
    payment.paid_at = timezone.now()
    if ref_id not in (None, ""):
        payment.tracking_code = str(ref_id)
    payment.save(update_fields=("status", "paid_at", "tracking_code"))


def _mark_payment_canceled(payment_id):
    _mark_payment_status(payment_id, PaymentStatus.CANCELED)


def _mark_payment_failed(payment_id):
    _mark_payment_status(payment_id, PaymentStatus.FAILED)


def _mark_payment_status(payment_id, status):
    with _atomic():
        payment = Payment.objects.select_for_update().get(pk=payment_id)
        if payment.status != PaymentStatus.PENDING:
            return
        payment.status = status
        payment.save(update_fields=("status",))

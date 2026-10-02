import logging

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from config.middleware import _tenant_local
from core.tasks import send_pattern_code_sms
from order.models import Order, OrderStatusMessage

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def remember_order_status(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_status = None
        return

    instance._previous_status = (
        Order.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    )


@receiver(post_save, sender=Order)
def queue_order_status_sms(sender, instance, created, update_fields=None, **kwargs):
    if update_fields is not None and 'status' not in update_fields:
        return

    previous_status = getattr(instance, '_previous_status', None)
    if created or previous_status is None or previous_status == instance.status:
        return

    message = OrderStatusMessage.objects.filter(status=instance.status, is_active=True).first()
    if message is None or not instance.user_id:
        return

    phone = instance.user.phone_number
    if not phone or not (message.pattern_code or '').strip():
        return

    parameters = message.parameters_for(instance)
    pattern_code = message.pattern_code.strip()
    log_type = f'order_{instance.status}'
    db_alias = getattr(_tenant_local, 'db', 'default')

    def enqueue():
        try:
            send_pattern_code_sms.delay(phone, pattern_code, parameters, log_type, db_alias)
        except Exception:
            logger.exception('Failed to enqueue order status SMS for order %s', instance.pk)

    transaction.on_commit(enqueue)

import logging

from celery import shared_task

from config.middleware import _tenant_local

logger = logging.getLogger(__name__)


def _run_on_tenant(db_alias, callback):
    _tenant_local.db = db_alias
    try:
        return callback()
    except Exception:
        logger.exception('SMS task failed')
        raise
    finally:
        if hasattr(_tenant_local, 'db'):
            del _tenant_local.db


@shared_task
def send_pattern_sms(phone, pattern_type, parameters=None, db_alias='default'):
    from core.services import SMSService

    return _run_on_tenant(
        db_alias,
        lambda: SMSService.send_pattern(phone, pattern_type, **(parameters or {})),
    )


@shared_task
def send_pattern_code_sms(phone, pattern_code, parameters=None, log_type='pattern', db_alias='default'):
    from core.services import SMSService

    return _run_on_tenant(
        db_alias,
        lambda: SMSService.send_by_pattern_code(
            phone,
            pattern_code,
            parameters or {},
            log_type,
        ),
    )


@shared_task
def notify_admins_sms(pattern_type, parameters=None, db_alias='default'):
    from core.services import SMSService

    return _run_on_tenant(
        db_alias,
        lambda: SMSService.deliver_notify_admins(pattern_type, **(parameters or {})),
    )

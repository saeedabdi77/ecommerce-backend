import logging

from celery import shared_task

from config.middleware import _tenant_local

logger = logging.getLogger(__name__)


@shared_task
def create_catalog_activity_log(
    event_type,
    user_id=None,
    query='',
    product_type_id=None,
    category_id=None,
    ip_address=None,
    user_agent='',
    db_alias='default',
):
    from product.models import CatalogActivityLog

    _tenant_local.db = db_alias
    try:
        CatalogActivityLog.objects.create(
            event_type=event_type,
            user_id=user_id,
            query=query or '',
            product_type_id=product_type_id,
            category_id=category_id,
            ip_address=ip_address,
            user_agent=user_agent or '',
        )
    except Exception:
        logger.exception('Failed to create catalog activity log')
        raise
    finally:
        if hasattr(_tenant_local, 'db'):
            del _tenant_local.db

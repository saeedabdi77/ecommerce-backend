import logging

from product.tasks import create_catalog_activity_log

logger = logging.getLogger(__name__)


def enqueue_catalog_activity(
    request,
    event_type,
    *,
    query='',
    product_type_id=None,
    category_id=None,
):
    user = getattr(request, 'user', None)
    user_id = user.pk if user is not None and user.is_authenticated else None

    try:
        create_catalog_activity_log.delay(
            event_type=event_type,
            user_id=user_id,
            query=query or '',
            product_type_id=product_type_id,
            category_id=category_id,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '') or '',
            db_alias=getattr(request, 'db_alias', 'default'),
        )
    except Exception:
        logger.exception('Failed to enqueue catalog activity log')

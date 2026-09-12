import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

celery = Celery("config")
celery.config_from_object("django.conf:settings", namespace="CELERY")
celery.autodiscover_tasks()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from order.tasks import expire_submitted_orders

    sender.add_periodic_task(
        crontab(minute="*/30"),
        expire_submitted_orders.s(),
    )
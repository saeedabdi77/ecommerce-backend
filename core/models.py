from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class BaseQuerySet(models.QuerySet):

    def delete(self):
        self.update(is_deleted=True)

    def force_delete(self):
        return super().delete()


class BaseModelManager(models.manager.BaseManager.from_queryset(BaseQuerySet)):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def get_queryset_with_deleted(self):
        return super().get_queryset()


class DeletedObjectsModelManager(models.manager.BaseManager.from_queryset(BaseQuerySet)):

    def get_queryset(self):
        return super().get_queryset()

    def get_queryset_with_deleted(self):
        return super().get_queryset()


class BaseModel(models.Model):
    created_at = models.DateTimeField('Created  at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    is_deleted = models.BooleanField('is deleted', default=False)
    extra = models.JSONField('Extra field', null=True, blank=True)

    objects = BaseModelManager()
    deleted_objects = DeletedObjectsModelManager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def force_delete(self, *args):
        return super().delete(*args)

    class Meta:
        abstract = True


class LogBaseModel(models.Model):
    created_at = models.DateTimeField('Created  at', auto_now_add=True)

    class Meta:
        abstract = True


class BaseSignalLogsModel(LogBaseModel):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    M2M_UPDATE = 'M2M_UPDATE'

    ACTIONS = (
        (CREATE, 'create'),
        (UPDATE, 'update'),
        (DELETE, 'delete'),
        (M2M_UPDATE, 'm2m_update'),
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    # request_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTIONS)

    class Meta:
        abstract = True

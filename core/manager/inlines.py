from django.core.exceptions import ImproperlyConfigured
from django.db import models


class Inline:
    model = None
    form_class = None
    fk_name = None
    fields = None
    extra = 1
    min_num = 0
    max_num = None
    can_delete = True
    verbose_name_plural = None

    def __init__(
        self,
        *,
        model=None,
        form_class=None,
        fk_name=None,
        fields=None,
        extra=1,
        min_num=0,
        max_num=None,
        can_delete=True,
        verbose_name_plural=None,
    ):
        self.model = model or self.model
        self.form_class = form_class or self.form_class
        self.fk_name = fk_name or self.fk_name
        self.fields = fields if fields is not None else self.fields
        self.extra = extra
        self.min_num = min_num
        self.max_num = max_num
        self.can_delete = can_delete
        self.verbose_name_plural = verbose_name_plural or self.verbose_name_plural

        if self.model is None:
            raise ImproperlyConfigured("Inline.model must be defined.")

        if self.form_class is None:
            raise ImproperlyConfigured("Inline.form_class must be defined.")

    def get_fk_name(self, parent_model):
        if self.fk_name:
            return self.fk_name

        fk_fields = [
            field.name
            for field in self.model._meta.get_fields()
            if isinstance(field, models.ForeignKey) and field.remote_field.model is parent_model
        ]

        if len(fk_fields) == 1:
            return fk_fields[0]

        if not fk_fields:
            raise ImproperlyConfigured(
                f"Could not find ForeignKey from {self.model.__name__} to {parent_model.__name__}."
            )

        raise ImproperlyConfigured(
            f"Multiple ForeignKeys from {self.model.__name__} to {parent_model.__name__}. "
            f"Set Inline.fk_name explicitly."
        )

    def get_verbose_name_plural(self):
        if self.verbose_name_plural:
            return self.verbose_name_plural

        return self.model._meta.verbose_name_plural

    def get_prefix(self, index):
        return f"inline{index}"

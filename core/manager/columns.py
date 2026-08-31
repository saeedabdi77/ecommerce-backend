from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


def boolean_badge(value):
    if value is True:
        return mark_safe('<span class="badge badge-success">بله</span>')
    if value is False:
        return mark_safe('<span class="badge badge-muted">خیر</span>')
    return ""


class Column:
    def __init__(
        self,
        name,
        label=None,
        *,
        value=None,
        formatter=None,
        editable=None,
        edit_widget=None,
        sortable=False,
        html=False,
        link_to_detail=False,
    ):
        self.name = name
        self.label = label or name.replace("_", " ").title()
        self.value = value
        self.formatter = formatter
        self.sortable = sortable
        self.editable = editable
        self.edit_widget = edit_widget
        self.html = html
        self.link_to_detail = link_to_detail

    @property
    def ordering_name(self):
        return self.name.replace(".", "__")

    def get_field_name(self):
        return self.name.split(".")[0]

    def get_model_field(self, model):
        try:
            return model._meta.get_field(self.get_field_name())
        except FieldDoesNotExist:
            return None

    def get_edit_widget(self, model):
        if self.edit_widget:
            return self.edit_widget

        if not self.editable:
            return None

        field = self.get_model_field(model)

        if isinstance(field, models.BooleanField):
            return "checkbox"

        if field is not None and getattr(field, "choices", None):
            return "select"

        if isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField, models.PositiveIntegerField)):
            return "number"

        return "text"

    def get_edit_choices(self, model):
        field = self.get_model_field(model)

        if field is not None and getattr(field, "choices", None):
            return list(field.flatchoices)

        return ()

    def get_value(self, obj):
        if self.value:
            return self.value(obj)

        value = obj

        for part in self.name.split("."):
            if value is None:
                return None

            value = getattr(value, part, None)

            if callable(value):
                value = value()

        return value

    def render(self, obj, model=None):
        value = self.get_value(obj)
        is_html = self.html

        if self.formatter:
            value = self.formatter(value, obj)
            is_html = True
        elif model is not None:
            model_field = self.get_model_field(model)

            if isinstance(model_field, models.BooleanField) and not self.editable:
                value = boolean_badge(value)
                is_html = True
            elif model_field is not None and getattr(model_field, "choices", None) and not self.editable:
                value = dict(model_field.flatchoices).get(value, value)

        if value is None:
            return ""

        return mark_safe(value) if is_html else conditional_escape(str(value))

    def get_edit_url(self, request, manager, obj):
        return manager.get_update_url(request, obj)

from django import forms
from django.core.exceptions import ValidationError

from core.manager.autocomplete import get_autocomplete_config, get_model_key, uses_autocomplete
from core.manager.widgets import AutocompleteSelect, AutocompleteSelectMultiple


class AutocompleteModelChoiceField(forms.ModelChoiceField):
    def __init__(self, *, queryset, search_fields=None, widget=None, **kwargs):
        model = queryset.model
        config = get_autocomplete_config(model)
        self.search_fields = search_fields or config["search_fields"]

        if widget is None:
            widget = AutocompleteSelect(
                app_label=model._meta.app_label,
                model_name=model._meta.model_name,
            )

        super().__init__(queryset=model._default_manager.none(), widget=widget, **kwargs)

    def prepare_value(self, value):
        if hasattr(value, "pk"):
            label = get_autocomplete_config(value._meta.model)["label"](value)
            self.widget.attrs["data-display-value"] = label
            return value.pk
        return super().prepare_value(value)

    def set_display_from_pk(self, pk):
        if not pk:
            return

        model = self.queryset.model
        queryset = model._default_manager.filter(pk=pk)
        config = get_autocomplete_config(model)

        if config["select_related"]:
            queryset = queryset.select_related(*config["select_related"])

        obj = queryset.first()

        if obj is not None:
            self.widget.attrs["data-display-value"] = config["label"](obj)

    def clean(self, value):
        if value in self.empty_values:
            return None

        key = get_model_key(self.queryset.model)
        model = self.queryset.model
        queryset = model._default_manager.filter(pk=value)

        config = get_autocomplete_config(model)
        if config["select_related"]:
            queryset = queryset.select_related(*config["select_related"])

        obj = queryset.first()
        if obj is None:
            raise ValidationError("گزینه انتخاب‌شده معتبر نیست.")

        return obj


class AutocompleteModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *, queryset, search_fields=None, widget=None, **kwargs):
        model = queryset.model
        config = get_autocomplete_config(model)
        self.search_fields = search_fields or config["search_fields"]

        if widget is None:
            widget = AutocompleteSelectMultiple(
                app_label=model._meta.app_label,
                model_name=model._meta.model_name,
            )

        super().__init__(queryset=model._default_manager.none(), widget=widget, **kwargs)

    def prepare_value(self, value):
        if not value:
            return value

        model = self.queryset.model
        label_fn = get_autocomplete_config(model)["label"]
        pks = [item.pk if hasattr(item, "pk") else item for item in value]
        objects = model._default_manager.filter(pk__in=pks)
        selected = [{"id": obj.pk, "label": label_fn(obj)} for obj in objects]
        self.widget.attrs["data-selected"] = selected
        return pks

    def clean(self, value):
        if not value:
            return self.queryset.model._default_manager.none()

        qs = self.queryset.model._default_manager.filter(pk__in=value)
        if qs.count() != len(value):
            raise ValidationError("برخی از گزینه‌های انتخاب‌شده معتبر نیستند.")

        return qs


def convert_field_to_autocomplete(field):
    model = field.queryset.model

    if not uses_autocomplete(model):
        return field

    if isinstance(field, forms.ModelMultipleChoiceField):
        return AutocompleteModelMultipleChoiceField(
            label=field.label,
            required=field.required,
            queryset=model._default_manager.all(),
            initial=field.initial,
        )

    if isinstance(field, forms.ModelChoiceField):
        return AutocompleteModelChoiceField(
            label=field.label,
            required=field.required,
            queryset=model._default_manager.all(),
            initial=field.initial,
        )

    return field

from django import forms

from core.manager.autocomplete import uses_autocomplete
from core.manager.fields import AutocompleteModelChoiceField, convert_field_to_autocomplete


class ConfirmationForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="تأیید")


class BulkActionForm(forms.Form):
    selected = forms.MultipleChoiceField(widget=forms.MultipleHiddenInput)


def get_form_fieldsets(form):
    fieldsets = getattr(form.Meta, "fieldsets", None)

    if fieldsets:
        result = []

        for title, options in fieldsets:
            fields = [form[field_name] for field_name in options["fields"] if field_name in form.fields]
            result.append((title, fields))

        return result

    return [(None, list(form))]


def apply_autocomplete(form):
    for field_name in list(form.fields.keys()):
        field = form.fields[field_name]

        if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)):
            if uses_autocomplete(field.queryset.model):
                form.fields[field_name] = convert_field_to_autocomplete(field)

                if form.instance.pk:
                    value = getattr(form.instance, field_name, None)
                    if value is not None:
                        if hasattr(value, "all"):
                            form.initial[field_name] = list(value.values_list("pk", flat=True))
                        else:
                            form.initial[field_name] = value.pk

    ensure_choice_widgets(form)
    return form


def get_model_field_choices(model_field):
    if model_field is None or not getattr(model_field, "choices", None):
        return None

    return list(model_field.flatchoices)


def ensure_choice_widgets(form):
    """Keep choice dropdowns in sync with the model field definition."""
    if not getattr(form, "_meta", None):
        return form

    for field_name, field in form.fields.items():
        if not isinstance(field, forms.ChoiceField):
            continue

        model_field = _get_model_field(form, field_name)
        choices = get_model_field_choices(model_field)

        if choices is None:
            if field.choices and hasattr(field.widget, "choices") and not field.widget.choices:
                field.widget.choices = field.choices
            continue

        field.choices = choices

        if hasattr(field.widget, "choices"):
            field.widget.choices = choices

    return form


def _get_model_field(form, field_name):
    if not getattr(form, "_meta", None):
        return None

    try:
        return form._meta.model._meta.get_field(field_name)
    except Exception:
        return None

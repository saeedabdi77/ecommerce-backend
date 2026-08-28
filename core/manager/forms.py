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
    for field_name, field in list(form.fields.items()):
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

    return form

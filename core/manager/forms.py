import json

from django import forms
from django.forms import inlineformset_factory

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


def build_inline_formsets(manager, parent_instance=None, data=None, files=None):
    inlines = manager.get_inlines(None)

    if not inlines:
        return []

    formsets = []

    for index, inline in enumerate(inlines):
        fk_name = inline.get_fk_name(manager.model)
        prefix = inline.get_prefix(index)

        factory_kwargs = {
            "form": inline.form_class,
            "extra": inline.extra,
            "min_num": inline.min_num,
            "can_delete": inline.can_delete,
        }

        if inline.max_num is not None:
            factory_kwargs["max_num"] = inline.max_num

        if inline.fields is not None:
            factory_kwargs["fields"] = inline.fields

        FormSet = inlineformset_factory(
            manager.model,
            inline.model,
            fk_name=fk_name,
            **factory_kwargs,
        )

        formset = FormSet(
            data=data,
            files=files,
            instance=parent_instance,
            prefix=prefix,
        )

        for form in formset.forms:
            apply_autocomplete(form)

        formsets.append({
            "inline": inline,
            "formset": formset,
            "prefix": prefix,
            "fk_name": fk_name,
        })

    return formsets


def inline_formsets_are_valid(inline_formsets):
    return all(item["formset"].is_valid() for item in inline_formsets)


def save_inline_formsets(inline_formsets):
    for item in inline_formsets:
        item["formset"].save()


def get_inline_detail_tables(manager, obj):
    tables = []

    for inline in manager.get_inlines(None):
        fk_name = inline.get_fk_name(manager.model)
        related_name = inline.model._meta.get_field(fk_name).remote_field.related_name
        children = getattr(obj, related_name).all() if related_name else inline.model.objects.filter(**{fk_name: obj})

        form_class = inline.form_class
        display_fields = _get_inline_display_fields(form_class, fk_name)
        field_labels = _get_inline_display_field_labels(form_class, fk_name)

        rows = []

        for child in children:
            form = form_class(instance=child)
            apply_autocomplete(form)
            rows.append({
                "object": child,
                "cells": [
                    {
                        "value": _format_inline_detail_value(form, field_name, child),
                        "css_class": "json-value" if field_name == "condition" else "",
                    }
                    for field_name in display_fields
                ],
            })

        tables.append({
            "inline": inline,
            "title": inline.get_verbose_name_plural(),
            "rows": rows,
            "field_labels": field_labels,
        })

    return tables


def _get_inline_display_fields(form_class, fk_name):
    form = form_class()
    return [name for name in form.fields if name != fk_name]


def _get_inline_display_field_labels(form_class, fk_name):
    form = form_class()
    return [
        form.fields[field_name].label
        for field_name in form.fields
        if field_name != fk_name
    ]


def _format_inline_detail_value(form, field_name, instance):
    field = form.fields[field_name]
    value = getattr(instance, field_name, None)

    if value is None or value == "":
        return "—"

    if hasattr(field, "choices") and field.choices:
        choices = dict(field.choices)
        return choices.get(value, value)

    if field_name == "condition" and isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, indent=2)

    return value

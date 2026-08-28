import json

from django import forms
from django.utils.html import format_html, format_html_join


class AutocompleteSelect(forms.Widget):
    input_type = "text"

    def __init__(self, *, app_label, model_name, attrs=None):
        super().__init__(attrs)
        self.app_label = app_label
        self.model_name = model_name

    def render(self, name, value, attrs=None, renderer=None):
        attrs = self.build_attrs(self.attrs, attrs)
        display_value = attrs.pop("data-display-value", "")
        hidden_attrs = self.build_attrs({
            "type": "hidden",
            "name": name,
            "class": "autocomplete-value",
            "value": value or "",
        })

        return format_html(
            '<div class="manager-autocomplete" data-app-label="{}" data-model-name="{}">'
            '<input type="text" class="autocomplete-search" value="{}" '
            'placeholder="حداقل ۲ حرف بنویسید..." autocomplete="off">'
            '<input{}>'
            '<div class="autocomplete-dropdown" hidden></div>'
            '</div>',
            self.app_label,
            self.model_name,
            display_value,
            forms.utils.flatatt(hidden_attrs),
        )

    class Media:
        js = ("manager/js/manager.js",)


class AutocompleteSelectMultiple(forms.Widget):
    def __init__(self, *, app_label, model_name, attrs=None):
        super().__init__(attrs)
        self.app_label = app_label
        self.model_name = model_name

    def render(self, name, value, attrs=None, renderer=None):
        attrs = self.build_attrs(self.attrs, attrs)
        selected = attrs.pop("data-selected", []) or []

        chips = format_html_join(
            "",
            (
                '<span class="autocomplete-chip" data-id="{}">'
                "{}"
                '<button type="button" class="autocomplete-chip-remove" aria-label="حذف">×</button>'
                "</span>"
            ),
            ((item["id"], item["label"]) for item in selected),
        )

        hidden_inputs = format_html_join(
            "",
            '<input type="hidden" name="{}" value="{}" class="autocomplete-value">',
            ((name, item["id"]) for item in selected),
        )

        selected_json = json.dumps(selected, ensure_ascii=False)

        return format_html(
            '<div class="manager-autocomplete manager-autocomplete-multiple" '
            'data-app-label="{}" data-model-name="{}" data-field-name="{}" '
            'data-selected="{}">'
            '<div class="autocomplete-selected">{}</div>'
            '<input type="text" class="autocomplete-search" '
            'placeholder="حداقل ۲ حرف بنویسید..." autocomplete="off">'
            '<div class="autocomplete-hidden-inputs">{}</div>'
            '<div class="autocomplete-dropdown" hidden></div>'
            '</div>',
            self.app_label,
            self.model_name,
            name,
            selected_json,
            chips,
            hidden_inputs,
        )

    def value_from_datadict(self, data, files, name):
        return data.getlist(name)

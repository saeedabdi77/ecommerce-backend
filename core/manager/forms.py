from django import forms


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

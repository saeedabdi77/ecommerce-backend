from django import forms


class ConfirmationForm(forms.Form):
    confirm = forms.BooleanField(required=True)


class BulkActionForm(forms.Form):
    selected = forms.MultipleChoiceField(required=False, widget=forms.MultipleHiddenInput)

from django import forms

from repair.models import RepairDeviceType, RepairProblemType, RepairRequest


class RepairDeviceTypeForm(forms.ModelForm):
    class Meta:
        model = RepairDeviceType
        fields = ("name", "active", "order")


class RepairProblemTypeForm(forms.ModelForm):
    class Meta:
        model = RepairProblemType
        fields = ("name", "device_types", "active", "order")
        widgets = {
            "device_types": forms.SelectMultiple(attrs={"size": 6, "full_width": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["device_types"].queryset = RepairDeviceType.objects.order_by("order", "name")


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = (
            "user",
            "name",
            "phone_number",
            "device_type",
            "problem_type",
            "description",
            "image",
            "status",
            "estimated_price",
            "final_price",
            "admin_note",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "full_width": True}),
            "admin_note": forms.Textarea(attrs={"rows": 3, "full_width": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["device_type"].queryset = RepairDeviceType.objects.order_by("order", "name")
        self.fields["problem_type"].queryset = RepairProblemType.objects.order_by("order", "name")

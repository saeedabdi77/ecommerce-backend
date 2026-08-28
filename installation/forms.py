from django import forms

from installation.models import Game, GameRate, InstallationDeviceType, InstallationRequest, InstallationRequestItem


class InstallationDeviceTypeForm(forms.ModelForm):
    class Meta:
        model = InstallationDeviceType
        fields = ("name", "active", "order")


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ("name", "device_type", "size", "price", "active", "image")
        widgets = {
            "device_type": forms.SelectMultiple(attrs={"size": 6, "full_width": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["device_type"].queryset = InstallationDeviceType.objects.order_by("order", "name")


class GameRateForm(forms.ModelForm):
    class Meta:
        model = GameRate
        fields = ("game", "source", "rate")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["game"].queryset = Game.objects.order_by("name")


class InstallationRequestForm(forms.ModelForm):
    class Meta:
        model = InstallationRequest
        fields = ("user", "guest_uid", "status", "device_type", "total_price", "admin_note")
        widgets = {
            "admin_note": forms.Textarea(attrs={"rows": 3, "full_width": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["device_type"].queryset = InstallationDeviceType.objects.order_by("order", "name")
        self.fields["total_price"].disabled = True


class InstallationRequestItemForm(forms.ModelForm):
    class Meta:
        model = InstallationRequestItem
        fields = ("installation_request", "game", "price")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["game"].queryset = Game.objects.order_by("name")

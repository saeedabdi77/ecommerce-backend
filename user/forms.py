from django import forms

from user.enums import LoginMethod
from user.models import Address, City, Province, User


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label="رمز عبور",
        required=False,
        widget=forms.PasswordInput(render_value=True),
    )

    class Meta:
        model = User
        fields = ("phone_number", "email", "first_name", "last_name", "is_staff", "is_active", "password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["password"].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_unusable_password()

        if commit:
            user.save()

        return user


class ProvinceForm(forms.ModelForm):
    class Meta:
        model = Province
        fields = ("name",)


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ("province", "name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["province"].queryset = Province.objects.order_by("name")


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            "user",
            "title",
            "city",
            "address_detail",
            "postal_code",
            "latitude",
            "longitude",
        )
        widgets = {
            "address_detail": forms.Textarea(attrs={"rows": 4, "full_width": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.order_by("phone_number")
        self.fields["city"].queryset = City.objects.select_related("province").order_by("province__name", "name")

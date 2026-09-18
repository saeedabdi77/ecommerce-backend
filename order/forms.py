import json

from django import forms
from django.core.exceptions import ValidationError

from order.models import DeliveryMethod, DeliveryPricing, Order, OrderItem, OrderItemProduct, OrderConfig
from product.models import Product, ProductType
from user.models import User


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("user", "guest_uid", "status", "total_price", "admin_note")
        widgets = {
            "admin_note": forms.Textarea(attrs={"rows": 3, "full_width": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.order_by("phone_number")
        self.fields["total_price"].disabled = True


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ("order", "product_type", "price", "count")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].queryset = Order.objects.order_by("-created_at")
        self.fields["product_type"].queryset = ProductType.objects.select_related("category", "brand").order_by("name")


class OrderItemProductForm(forms.ModelForm):
    class Meta:
        model = OrderItemProduct
        fields = ("order_item", "product")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order_item"].queryset = OrderItem.objects.select_related("order", "product_type").order_by("-created_at")
        self.fields["product"].queryset = Product.objects.select_related("product_type").order_by("-id")



class OrderConfigForm(forms.ModelForm):
    class Meta:
        model = OrderConfig
        fields = ("registration_enabled", "reservation_duration")


class DeliveryMethodForm(forms.ModelForm):
    class Meta:
        model = DeliveryMethod
        fields = ("name", "description", "delivery_time", "is_active", "is_tehran_city_only")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "full_width": True}),
        }


class DeliveryPricingInlineForm(forms.ModelForm):
    condition = forms.CharField(
        label="شرط",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "dir": "ltr",
                "placeholder": '{"min": 0, "max": 100000}',
                "class": "inline-json-field",
                "spellcheck": "false",
                "autocomplete": "off",
            },
        ),
    )

    class Meta:
        model = DeliveryPricing
        fields = ("strategy", "condition", "price")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and isinstance(self.instance.condition, dict):
            self.initial["condition"] = json.dumps(
                self.instance.condition,
                ensure_ascii=False,
                indent=2,
            )

    def clean_condition(self):
        value = self.cleaned_data.get("condition")

        if value in (None, ""):
            return {}

        if isinstance(value, dict):
            return value

        try:
            parsed = json.loads(value)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValidationError("شرط باید یک JSON معتبر باشد.") from exc

        if not isinstance(parsed, dict):
            raise ValidationError("شرط باید یک شیء JSON باشد.")

        return parsed

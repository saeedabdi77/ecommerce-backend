import json
import re

from django import forms
from django.core.exceptions import ValidationError

from order.enums import OrderStatus
from order.models import (
    DeliveryMethod,
    DeliveryPricing,
    Order,
    OrderItem,
    OrderItemProduct,
    OrderConfig,
    OrderStatusMessage,
)
from order.utilities import register_order_products
from product.enums import ProductState
from product.models import Product, ProductType
from user.models import User


class OrderForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        label="کالاها",
        queryset=Product.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"full_width": True, "size": 8}),
    )

    class Meta:
        model = Order
        fields = (
            "user",
            "first_name",
            "last_name",
            "buyer_phone",
            "buyer_address",
            "sale_method",
            "status",
            "products",
            "delivery_method",
            "delivery_cost",
            "admin_note",
            "total_price",
        )
        widgets = {
            "buyer_address": forms.Textarea(attrs={"rows": 3, "full_width": True}),
            "admin_note": forms.Textarea(attrs={"rows": 3, "full_width": True}),
        }
        fieldsets = (
            ("خریدار", {"fields": ("user", "first_name", "last_name", "buyer_phone", "buyer_address")}),
            ("سفارش", {"fields": ("sale_method", "status", "products", "delivery_method", "delivery_cost", "admin_note")}),
            ("مبلغ", {"fields": ("total_price",)}),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._register_products = self.instance.pk is None
        self.fields["user"].required = False
        self.fields["user"].queryset = User.objects.order_by("phone_number")
        self.fields["user"].help_text = "اگر خریدار حساب ندارد، خالی بگذارید و نام، نام خانوادگی و موبایل را بنویسید."
        self.fields["first_name"].required = False
        self.fields["last_name"].required = False
        self.fields["buyer_phone"].required = False
        self.fields["delivery_method"].required = False
        self.fields["delivery_method"].queryset = DeliveryMethod.objects.filter(is_active=True).order_by("name")
        self.fields["delivery_cost"].required = False
        self.fields["total_price"].disabled = True

        if self._register_products:
            self.initial["status"] = OrderStatus.PAID
            self.fields["status"].help_text = "پرداخت‌شده کالا را فروخته می‌کند. ثبت‌شده فقط رزرو می‌کند."
            self.fields["products"].queryset = Product.objects.filter(
                state=ProductState.IN_WAREHOUSE,
            ).select_related("product_type")
            self.fields["products"].required = True
            self.fields["products"].help_text = "فقط کالای داخل انبار."
        else:
            self.fields.pop("products", None)

    def clean_delivery_cost(self):
        value = self.cleaned_data.get("delivery_cost")
        return 0 if value in (None, "") else value

    def clean_first_name(self):
        return (self.cleaned_data.get("first_name") or "").strip()

    def clean_last_name(self):
        return (self.cleaned_data.get("last_name") or "").strip()

    def clean_buyer_phone(self):
        phone = (self.cleaned_data.get("buyer_phone") or "").strip()
        if phone and not re.fullmatch(r"09\d{9}", phone):
            raise forms.ValidationError("شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.")
        return phone

    def clean_products(self):
        products = list(self.cleaned_data.get("products") or [])
        if any(product.state != ProductState.IN_WAREHOUSE for product in products):
            raise forms.ValidationError("فقط کالای موجود در انبار را می‌توان به سفارش اضافه کرد.")
        return products

    def clean(self):
        cleaned = super().clean()
        if not self._register_products:
            return cleaned

        if cleaned.get("status") in (OrderStatus.DRAFT, OrderStatus.CANCELED):
            self.add_error("status", "برای ثبت سفارش، وضعیت را پرداخت‌شده یا ثبت‌شده بگذارید.")
        if not cleaned.get("user") and not (
            cleaned.get("first_name") and cleaned.get("last_name") and cleaned.get("buyer_phone")
        ):
            self.add_error("first_name", "اگر کاربر انتخاب نشده، نام، نام خانوادگی و موبایل خریدار لازم است.")
        return cleaned

    def save(self, commit=True):
        register = self._register_products
        order = super().save(commit=commit)
        if commit and register and self.cleaned_data.get("products"):
            register_order_products(order, self.cleaned_data["products"])
        return order


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ("order", "product_type", "price", "dollar_price", "count")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].queryset = Order.objects.order_by("-created_at")
        self.fields["product_type"].queryset = ProductType.objects.select_related("category", "brand").order_by("name")
        self.fields["dollar_price"].disabled = True
        self.fields["dollar_price"].help_text = "هنگام ثبت سفارش از قیمت دلار در تنظیمات سایت پر می‌شود."


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


class OrderStatusMessageForm(forms.ModelForm):
    class Meta:
        model = OrderStatusMessage
        fields = (
            "name",
            "status",
            "pattern_code",
            "is_active",
            "tracking_code_param",
            "full_name_param",
        )
        widgets = {
            "pattern_code": forms.TextInput(attrs={"dir": "ltr"}),
            "tracking_code_param": forms.TextInput(attrs={"dir": "ltr"}),
            "full_name_param": forms.TextInput(attrs={"dir": "ltr"}),
        }
        fieldsets = (
            ("پیام", {"fields": ("name", "status", "pattern_code", "is_active")}),
            ("متغیرهای پترن", {"fields": ("tracking_code_param", "full_name_param")}),
        )


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

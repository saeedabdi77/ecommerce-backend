from django import forms

from order.models import Order, OrderItem, OrderItemProduct
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

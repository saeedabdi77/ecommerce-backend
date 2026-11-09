from django import forms

from core.site_config import get_dollar_price
from product.enums import ProductState
from product.models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductCollection,
    ProductImage,
    ProductType,
    PurchaseMethod,
    Review,
    Tag,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("parent", "name", "slug", "image", "icon", "homepage_show", "order", "seo_keywords", "seo_description")
        widgets = {
            "seo_keywords": forms.Textarea(attrs={"rows": 3}),
            "seo_description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["parent"].queryset = Category.objects.exclude(pk=self.instance.pk)


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ("name", "slug", "logo", "is_active")


class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ("name", "slug")


class AttributeValueForm(forms.ModelForm):
    class Meta:
        model = AttributeValue
        fields = ("attribute", "value", "slug")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attribute"].queryset = Attribute.objects.order_by("name")


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name", "slug")


class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = (
            "category",
            "brand",
            "name",
            "description",
            "active",
            "main_price",
            "sell_price",
            "weight",
            "dimensions",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "tags",
        )
        labels = {
            "category": "Category",
            "brand": "Brand",
            "name": "Name",
            "description": "Description",
            "active": "Active",
            "main_price": "Main price",
            "sell_price": "Sell price",
            "weight": "Weight (g)",
            "dimensions": "Dimensions (cm)",
            "seo_title": "SEO title",
            "seo_description": "SEO description",
            "seo_keywords": "SEO keywords",
            "tags": "Tags",
        }
        help_texts = {
            "name": "English name. The slug is created from this.",
            "main_price": "English digits.",
            "sell_price": "English digits. Cannot be higher than the main price.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"dir": "ltr", "placeholder": "Gold ring"}),
            "description": forms.Textarea(attrs={"rows": 5, "full_width": True, "dir": "ltr"}),
            "main_price": forms.TextInput(attrs={"dir": "ltr", "inputmode": "numeric", "placeholder": "2500000"}),
            "sell_price": forms.TextInput(attrs={"dir": "ltr", "inputmode": "numeric", "placeholder": "1990000"}),
            "weight": forms.TextInput(attrs={"dir": "ltr", "inputmode": "decimal"}),
            "dimensions": forms.TextInput(attrs={"dir": "ltr", "placeholder": "20x15x10"}),
            "seo_title": forms.TextInput(attrs={"dir": "ltr"}),
            "seo_description": forms.Textarea(attrs={"rows": 4, "full_width": True, "dir": "ltr"}),
            "seo_keywords": forms.Textarea(attrs={"rows": 3, "full_width": True, "dir": "ltr"}),
            "tags": forms.SelectMultiple(attrs={"size": 6, "full_width": True}),
        }
        fieldsets = (
            ("Product", {"fields": ("category", "brand", "name", "description", "active")}),
            ("Prices", {"fields": ("main_price", "sell_price")}),
            ("Details", {"fields": ("weight", "dimensions")}),
            ("SEO", {"fields": ("seo_title", "seo_description", "seo_keywords")}),
            ("Tags", {"fields": ("tags",)}),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.order_by("order", "name")
        self.fields["brand"].queryset = Brand.objects.filter(is_active=True).order_by("name")
        self.fields["brand"].required = False
        self.fields["tags"].queryset = Tag.objects.order_by("name")
        self.fields["tags"].required = False

    def clean_sell_price(self):
        sell_price = self.cleaned_data["sell_price"]
        main_price = self.cleaned_data.get("main_price")

        if main_price is not None and sell_price > main_price:
            raise forms.ValidationError("Sell price cannot be higher than the main price.")

        return sell_price


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ("product_type", "attribute_value", "extra_price")


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ("product_type", "image", "is_thumbnail", "order")


class ProductImageInlineForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ("image", "is_thumbnail", "order")
        labels = {
            "image": "Image",
            "is_thumbnail": "Thumbnail",
            "order": "Order",
        }


class PurchaseMethodForm(forms.ModelForm):
    class Meta:
        model = PurchaseMethod
        fields = ("name", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ProductInlineForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("purchase_price", "purchase_method", "serial", "state")
        labels = {
            "purchase_price": "Purchase price",
            "purchase_method": "Purchase method",
            "serial": "Serial",
            "state": "State",
        }
        widgets = {
            "purchase_price": forms.TextInput(attrs={"dir": "ltr", "inputmode": "numeric", "placeholder": "800000"}),
            "serial": forms.TextInput(attrs={"dir": "ltr", "placeholder": "SN-1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["purchase_method"].required = False
        self.fields["purchase_method"].queryset = PurchaseMethod.objects.order_by("name")
        self.fields["serial"].required = False
        self.fields["state"].choices = (
            (ProductState.IN_WAREHOUSE, "In warehouse"),
            (ProductState.RESERVED, "Reserved"),
            (ProductState.SOLD, "Sold"),
            (ProductState.LOST, "Lost"),
        )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("product_type", "purchase_price", "purchase_method", "dollar_price", "serial", "state")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product_type"].queryset = ProductType.objects.select_related("category", "brand").order_by("name")
        self.fields["purchase_method"].queryset = PurchaseMethod.objects.order_by("name")
        self.fields["purchase_method"].required = True
        self.fields["dollar_price"].disabled = True
        self.fields["dollar_price"].help_text = "هنگام ثبت کالا از قیمت دلار در تنظیمات سایت پر می‌شود."
        if not self.instance.pk:
            self.initial["dollar_price"] = get_dollar_price()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("product_type", "user", "rating", "title", "comment", "is_verified", "is_approved")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 5}),
        }


class ProductCollectionForm(forms.ModelForm):
    class Meta:
        model = ProductCollection
        fields = (
            "name",
            "code_name",
            "product_types",
            "is_active",
            "order",
            "description",
            "image",
            "seo_title",
            "seo_description",
        )
        widgets = {
            "product_types": forms.SelectMultiple(attrs={"size": 10}),
            "description": forms.Textarea(attrs={"rows": 5}),
            "seo_description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product_types"].queryset = ProductType.objects.select_related("category", "brand").order_by("name")

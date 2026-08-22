from django import forms

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
            "slug",
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
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "seo_description": forms.Textarea(attrs={"rows": 4}),
            "seo_keywords": forms.Textarea(attrs={"rows": 3}),
            "tags": forms.SelectMultiple(attrs={"size": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.order_by("order", "name")
        self.fields["brand"].queryset = Brand.objects.filter(is_active=True).order_by("name")
        self.fields["tags"].queryset = Tag.objects.order_by("name")

    def clean_sell_price(self):
        sell_price = self.cleaned_data["sell_price"]
        main_price = self.cleaned_data.get("main_price")

        if main_price is not None and sell_price > main_price:
            raise forms.ValidationError("قیمت فروش نمی‌تواند از قیمت اصلی بیشتر باشد")

        return sell_price


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ("product_type", "attribute_value", "extra_price")


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ("product_type", "image", "is_thumbnail", "order")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("product_type", "purchase_price", "serial", "state")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product_type"].queryset = ProductType.objects.select_related("category", "brand").order_by("name")


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

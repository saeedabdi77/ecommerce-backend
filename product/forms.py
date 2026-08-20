from django.forms import ModelForm

from product.models import ProductType, Category, Brand


class ProductTypeForm(ModelForm):
    class Meta:
        model = ProductType
        fields = "__all__"


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class BrandForm(ModelForm):
    class Meta:
        model = Brand
        fields = "__all__"

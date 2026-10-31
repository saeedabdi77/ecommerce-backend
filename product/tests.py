from django.test import TestCase

from core.models import SiteSettings
from product.enums import ProductState
from product.forms import ProductForm
from product.models import Brand, Category, Product, ProductType


def site_settings(**kwargs):
    settings = SiteSettings.objects.order_by("pk").first()
    if settings is None:
        defaults = {
            "mediana_api_key": "key",
            "mediana_from_number": "1000",
        }
        defaults.update(kwargs)
        return SiteSettings.objects.create(**defaults)

    for field, value in kwargs.items():
        setattr(settings, field, value)
    if kwargs:
        settings.save(update_fields=tuple(kwargs))
    return settings


class ProductDollarPriceTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Rings", slug="rings")
        brand = Brand.objects.create(name="Atashin", slug="atashin")
        self.product_type = ProductType.objects.create(
            category=category,
            brand=brand,
            name="Ring",
            slug="ring",
            description="A ring",
            main_price=200,
            sell_price=150,
        )

    def test_new_product_stores_dollar_price_from_config(self):
        site_settings(dollar_price=85000)

        product = Product.objects.create(
            product_type=self.product_type,
            purchase_price=80,
            state=ProductState.IN_WAREHOUSE,
        )

        self.assertEqual(product.dollar_price, 85000)

    def test_new_product_without_config_leaves_dollar_price_empty(self):
        product = Product.objects.create(
            product_type=self.product_type,
            purchase_price=80,
            state=ProductState.IN_WAREHOUSE,
        )

        self.assertIsNone(product.dollar_price)

    def test_later_config_change_does_not_change_existing_product(self):
        settings = site_settings(dollar_price=85000)
        product = Product.objects.create(
            product_type=self.product_type,
            purchase_price=80,
            state=ProductState.IN_WAREHOUSE,
        )

        settings.dollar_price = 91000
        settings.save(update_fields=("dollar_price",))
        product.purchase_price = 90
        product.save(update_fields=("purchase_price",))

        product.refresh_from_db()
        self.assertEqual(product.dollar_price, 85000)

    def test_product_form_stores_dollar_price_from_config(self):
        site_settings(dollar_price=85000)
        form = ProductForm(data={
            "product_type": self.product_type.pk,
            "purchase_price": 80,
            "serial": "SN-1",
            "state": ProductState.IN_WAREHOUSE,
        })

        self.assertTrue(form.is_valid(), form.errors)
        product = form.save()

        self.assertEqual(product.dollar_price, 85000)

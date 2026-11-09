import tempfile
from io import BytesIO

from decouple import config
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from core.manager.forms import build_inline_formsets, inline_formsets_are_valid, save_inline_formsets
from core.models import SiteSettings
from product.enums import ProductState
from product.forms import ProductForm, ProductTypeForm
from product.managers import ProductTypeManager
from product.models import Brand, Category, Product, ProductImage, ProductType, PurchaseMethod
from user.models import User


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
        method = PurchaseMethod.objects.create(name="Cash")
        form = ProductForm(data={
            "product_type": self.product_type.pk,
            "purchase_price": 80,
            "purchase_method": method.pk,
            "serial": "SN-1",
            "state": ProductState.IN_WAREHOUSE,
        })

        self.assertTrue(form.is_valid(), form.errors)
        product = form.save()

        self.assertEqual(product.dollar_price, 85000)
        self.assertEqual(product.purchase_method_id, method.pk)

    def test_product_form_requires_purchase_method(self):
        form = ProductForm(data={
            "product_type": self.product_type.pk,
            "purchase_price": 80,
            "serial": "SN-2",
            "state": ProductState.IN_WAREHOUSE,
        })

        self.assertFalse(form.is_valid())
        self.assertIn("purchase_method", form.errors)


def tiny_png(name="ring.png"):
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class ProductTypeEntryTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.brand = Brand.objects.create(name="Atashin", slug="atashin")

    def test_slug_is_generated_from_the_english_name(self):
        product_type = ProductType.objects.create(
            category=self.category,
            name="Gold Ring",
            description="A gold ring",
            main_price=2500000,
            sell_price=1990000,
        )

        self.assertEqual(product_type.slug, "gold-ring")

    def test_duplicate_english_name_gets_a_unique_slug(self):
        shared = dict(
            category=self.category,
            name="Gold Ring",
            description="A gold ring",
            main_price=2500000,
            sell_price=1990000,
        )
        ProductType.objects.create(**shared)
        second = ProductType.objects.create(**shared)

        self.assertEqual(second.slug, "gold-ring-2")

    def test_existing_slug_is_kept_when_the_name_changes(self):
        product_type = ProductType.objects.create(
            category=self.category,
            name="Gold Ring",
            slug="custom-ring",
            description="A gold ring",
            main_price=2500000,
            sell_price=1990000,
        )
        product_type.name = "Silver Ring"
        product_type.save()

        self.assertEqual(product_type.slug, "custom-ring")

    def test_form_hides_slug_and_rejects_a_higher_sell_price(self):
        form = ProductTypeForm(data=self.product_type_data(sell_price="3000000", main_price="2000000"))

        self.assertNotIn("slug", form.fields)
        self.assertEqual(form.fields["main_price"].label, "Main price")
        self.assertEqual(form.fields["sell_price"].label, "Sell price")
        self.assertFalse(form.is_valid())
        self.assertIn("sell_price", form.errors)

    def test_empty_product_and_image_rows_can_be_left_blank(self):
        form = ProductTypeForm(data=self.product_type_data())
        formsets = build_inline_formsets(
            ProductTypeManager(),
            data=self.product_type_data(),
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(inline_formsets_are_valid(formsets), [item["formset"].errors for item in formsets])

        product_type = form.save()
        for item in formsets:
            item["formset"].instance = product_type
        save_inline_formsets(formsets)

        product_type.refresh_from_db()
        self.assertEqual(product_type.slug, "gold-ring")
        self.assertEqual(product_type.products.count(), 0)
        self.assertEqual(product_type.images.count(), 0)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_create_form_saves_product_image_and_english_prices(self):
        data = self.product_type_data()
        data.update({
            "inline0-0-purchase_price": "800000",
            "inline0-0-serial": "SN-1",
            "inline0-0-state": ProductState.IN_WAREHOUSE,
            "inline1-0-is_thumbnail": "on",
            "inline1-0-order": "1",
        })
        files = {"inline1-0-image": tiny_png()}
        form = ProductTypeForm(data=data, files=files)
        formsets = build_inline_formsets(ProductTypeManager(), data=data, files=files)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(inline_formsets_are_valid(formsets), [item["formset"].errors for item in formsets])

        product_type = form.save()
        for item in formsets:
            item["formset"].instance = product_type
        save_inline_formsets(formsets)

        product = product_type.products.get()
        image = product_type.images.get()
        self.assertEqual(product.purchase_price, 800000)
        self.assertEqual(product.serial, "SN-1")
        self.assertEqual(product.state, ProductState.IN_WAREHOUSE)
        self.assertIsInstance(image, ProductImage)
        self.assertTrue(image.is_thumbnail)
        self.assertTrue(image.image.name)

    def test_product_row_count_creates_that_many_items(self):
        data = self.product_type_data()
        data.update({
            "inline0-0-purchase_price": "800000",
            "inline0-0-serial": "SN-1",
            "inline0-0-state": ProductState.IN_WAREHOUSE,
            "inline0-0-count": "3",
        })
        form = ProductTypeForm(data=data)
        formsets = build_inline_formsets(ProductTypeManager(), data=data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(inline_formsets_are_valid(formsets), [item["formset"].errors for item in formsets])

        product_type = form.save()
        for item in formsets:
            item["formset"].instance = product_type
        save_inline_formsets(formsets)

        products = list(product_type.products.order_by("id"))
        self.assertEqual(len(products), 3)
        self.assertTrue(all(product.purchase_price == 800000 for product in products))
        self.assertTrue(all(product.serial == "SN-1" for product in products))
        self.assertTrue(all(product.state == ProductState.IN_WAREHOUSE for product in products))

    def product_type_data(self, **overrides):
        data = {
            "category": self.category.pk,
            "brand": self.brand.pk,
            "name": "Gold Ring",
            "description": "A plain gold ring",
            "active": "on",
            "main_price": "2500000",
            "sell_price": "1990000",
            "inline0-TOTAL_FORMS": "1",
            "inline0-INITIAL_FORMS": "0",
            "inline0-MIN_NUM_FORMS": "0",
            "inline0-MAX_NUM_FORMS": "1000",
            "inline0-0-purchase_price": "",
            "inline0-0-purchase_method": "",
            "inline0-0-serial": "",
            "inline0-0-state": ProductState.IN_WAREHOUSE,
            "inline1-TOTAL_FORMS": "1",
            "inline1-INITIAL_FORMS": "0",
            "inline1-MIN_NUM_FORMS": "0",
            "inline1-MAX_NUM_FORMS": "1000",
            "inline1-0-order": "10",
        }
        data.update(overrides)
        return data


class ProductTypeAdminPageTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Rings", slug="rings")
        self.user = User.objects.create(phone_number="09120000000", is_superuser=True, is_staff=True)
        self.client.force_login(self.user)

    def test_create_page_offers_products_images_and_english_prices(self):
        response = self.client.get(f"/{config('MANAGER_URL')}/default/product-types/create/")

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Main price", body)
        self.assertIn("Sell price", body)
        self.assertIn("Products", body)
        self.assertIn("Images", body)
        self.assertIn("Count", body)
        self.assertIn('dir="ltr"', body)
        self.assertNotIn('name="slug"', body)

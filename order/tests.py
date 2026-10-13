import uuid

from django.test import TestCase

from order.enums import OrderStatus
from order.models import Order, OrderItem
from order.utilities import sync_draft_order
from product.enums import ProductState
from product.models import Brand, Category, Product, ProductType


class DraftPriceSyncTests(TestCase):
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
        Product.objects.create(
            product_type=self.product_type,
            purchase_price=80,
            state=ProductState.IN_WAREHOUSE,
        )
        self.order = Order.objects.create(guest_uid=uuid.uuid4(), total_price=80)
        self.item = OrderItem.objects.create(
            order=self.order,
            product_type=self.product_type,
            price=80,
            count=1,
        )

    def test_draft_sync_copies_changed_sell_price_and_total(self):
        order = sync_draft_order(self.order)

        self.item.refresh_from_db()
        self.assertEqual(self.item.price, 150)
        self.assertEqual(order.total_price, 150)

    def test_unchanged_draft_price_does_not_write_item_or_total(self):
        self.item.price = 150
        self.item.save(update_fields=("price",))
        self.order.total_price = 150
        self.order.save(update_fields=("total_price",))

        self.item.refresh_from_db()
        self.order.refresh_from_db()
        item_updated_at = self.item.updated_at
        order_updated_at = self.order.updated_at

        sync_draft_order(self.order)

        self.item.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.item.updated_at, item_updated_at)
        self.assertEqual(self.order.updated_at, order_updated_at)
        self.assertEqual(self.item.price, 150)
        self.assertEqual(self.order.total_price, 150)

    def test_draft_sync_removes_inactive_product_and_deletes_empty_order(self):
        self.product_type.active = False
        self.product_type.save(update_fields=("active",))

        result = sync_draft_order(self.order)

        self.assertIsNone(result)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())
        self.assertFalse(OrderItem.objects.filter(pk=self.item.pk).exists())

    def test_draft_sync_drops_only_the_inactive_line(self):
        other_type = ProductType.objects.create(
            category=self.product_type.category,
            brand=self.product_type.brand,
            name="Necklace",
            slug="necklace",
            description="A necklace",
            main_price=90,
            sell_price=40,
        )
        Product.objects.create(
            product_type=other_type,
            purchase_price=20,
            state=ProductState.IN_WAREHOUSE,
        )
        other_item = OrderItem.objects.create(
            order=self.order,
            product_type=other_type,
            price=10,
            count=1,
        )
        self.product_type.active = False
        self.product_type.save(update_fields=("active",))

        order = sync_draft_order(self.order)

        self.assertFalse(OrderItem.objects.filter(pk=self.item.pk).exists())
        other_item.refresh_from_db()
        self.assertEqual(other_item.price, 40)
        self.assertEqual(order.total_price, 40)
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists())

    def test_submitted_order_keeps_inactive_product(self):
        self.order.status = OrderStatus.SUBMITTED
        self.order.save(update_fields=("status",))
        self.product_type.active = False
        self.product_type.save(update_fields=("active",))

        order = sync_draft_order(self.order)

        self.item.refresh_from_db()
        self.assertEqual(order.pk, self.order.pk)
        self.assertEqual(self.item.price, 80)
        self.assertEqual(self.order.total_price, 80)

    def test_submitted_order_keeps_item_price(self):
        self.order.status = OrderStatus.SUBMITTED
        self.order.save(update_fields=("status",))
        self.product_type.sell_price = 180
        self.product_type.save(update_fields=("sell_price",))

        sync_draft_order(self.order)

        self.item.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.item.price, 80)
        self.assertEqual(self.order.total_price, 80)

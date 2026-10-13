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

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config.middleware import _tenant_local
from product.enums import ProductState
from product.models import (
    Brand,
    Category,
    Product,
    ProductCollection,
    ProductImage,
    ProductType,
)


FONT_PATH = Path(settings.BASE_DIR) / "brand" / "fonts" / "PlayfairDisplay-Medium.ttf"

PARENT_CATEGORIES = [
    {
        "slug": "women",
        "name": "زنانه",
        "order": 10,
        "seo_keywords": "زیورآلات زنانه، جواهر فشن زنانه، ماریا",
        "seo_description": "انگشتر، گوشواره، گردنبند، دستبند و ست‌های زنانه ماریا.",
    },
    {
        "slug": "men",
        "name": "مردانه",
        "order": 20,
        "seo_keywords": "زیورآلات مردانه، انگشتر مردانه، گردنبند مردانه",
        "seo_description": "انگشتر، گردنبند، دستبند و گوشواره مردانه ماریا.",
    },
]

CATEGORIES = [
    {
        "slug": "rings",
        "parent": "women",
        "name": "انگشتر",
        "order": 10,
        "seo_keywords": "انگشتر زنانه، انگشتر فشن، انگشتر استیل",
        "seo_description": "انگشترهای زنانه ماریا؛ ظریف، روزمره و مناسب هدیه.",
    },
    {
        "slug": "earrings",
        "parent": "women",
        "name": "گوشواره",
        "order": 20,
        "seo_keywords": "گوشواره زنانه، گوشواره میخی، گوشواره آویز",
        "seo_description": "گوشواره میخی، آویز و حلقه‌ای زنانه با آبکاری طلایی، نقره‌ای و رزگلد.",
    },
    {
        "slug": "necklaces",
        "parent": "women",
        "name": "گردنبند",
        "order": 30,
        "seo_keywords": "گردنبند زنانه، پلاک، گردنبند مروارید",
        "seo_description": "گردنبندهای کوتاه و زنجیر ظریف زنانه برای استایل روز و مهمانی.",
    },
    {
        "slug": "bracelets",
        "parent": "women",
        "name": "دستبند",
        "order": 40,
        "seo_keywords": "دستبند زنانه، النگو، دستبند زنجیری",
        "seo_description": "دستبند زنجیری، بافت و مهره‌ای زنانه با حس دریا و استایل مینیمال.",
    },
    {
        "slug": "anklets",
        "parent": "women",
        "name": "پابند",
        "order": 50,
        "seo_keywords": "پابند زنانه، پابند زنجیری",
        "seo_description": "پابندهای سبک زنانه برای استایل تابستانی.",
    },
    {
        "slug": "sets",
        "parent": "women",
        "name": "ست",
        "order": 60,
        "seo_keywords": "ست زنانه، ست گردنبند گوشواره",
        "seo_description": "ست‌های هماهنگ گردنبند و گوشواره زنانه برای هدیه و مهمانی.",
    },
    {
        "slug": "men-rings",
        "parent": "men",
        "name": "انگشتر",
        "order": 10,
        "seo_keywords": "انگشتر مردانه، انگشتر استیل مردانه",
        "seo_description": "انگشترهای پهن و ساده مردانه از استیل ضدحساسیت.",
    },
    {
        "slug": "men-necklaces",
        "parent": "men",
        "name": "گردنبند",
        "order": 20,
        "seo_keywords": "گردنبند مردانه، زنجیر مردانه",
        "seo_description": "زنجیر و گردنبند مردانه با فرم ساده و سنگین‌تر.",
    },
    {
        "slug": "men-bracelets",
        "parent": "men",
        "name": "دستبند",
        "order": 30,
        "seo_keywords": "دستبند مردانه، دستبند زنجیری مردانه",
        "seo_description": "دستبند زنجیری مردانه برای استایل روزمره.",
    },
    {
        "slug": "men-earrings",
        "parent": "men",
        "name": "گوشواره",
        "order": 40,
        "seo_keywords": "گوشواره مردانه، حلقه مردانه",
        "seo_description": "گوشواره حلقه‌ای کوچک مردانه.",
    },
]

METALS = {
    "gold": (201, 162, 91),
    "silver": (184, 192, 196),
    "rose": (201, 137, 123),
    "steel": (138, 148, 153),
}

PRODUCTS = [
    {
        "slug": "maria-sample-thin-gold-ring",
        "name": "انگشتر باریک طلایی نمونه",
        "category": "rings",
        "kind": "ring",
        "metal": "gold",
        "description": "نمونه نمایشی. انگشتر باریک روزمره برای تست صفحه محصول.",
        "main_price": 980000,
        "sell_price": 890000,
        "weight": "3.20",
        "purchase_price": 420000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-pearl-ring",
        "name": "انگشتر مروارید نمونه",
        "category": "rings",
        "kind": "ring",
        "metal": "rose",
        "description": "نمونه نمایشی. انگشتر ظریف با فرم مروارید برای تست لیست زنانه.",
        "main_price": 1350000,
        "sell_price": 1250000,
        "weight": "3.50",
        "purchase_price": 580000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-star-earrings",
        "name": "گوشواره میخی ستاره نمونه",
        "category": "earrings",
        "kind": "earrings",
        "metal": "gold",
        "description": "نمونه نمایشی. گوشواره میخی سبک برای تست کارت محصول.",
        "main_price": 720000,
        "sell_price": 650000,
        "weight": "2.40",
        "purchase_price": 280000,
        "stock": 3,
    },
    {
        "slug": "maria-sample-drop-earrings",
        "name": "گوشواره آویز قطره نمونه",
        "category": "earrings",
        "kind": "earrings",
        "metal": "rose",
        "description": "نمونه نمایشی. گوشواره آویز برای تست گالری تصاویر.",
        "main_price": 890000,
        "sell_price": 790000,
        "weight": "4.60",
        "purchase_price": 360000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-thin-necklace",
        "name": "گردنبند زنجیر ظریف نمونه",
        "category": "necklaces",
        "kind": "necklace",
        "metal": "gold",
        "description": "نمونه نمایشی. گردنبند کوتاه برای تست فیلتر دسته‌بندی.",
        "main_price": 1250000,
        "sell_price": 1150000,
        "weight": "6.20",
        "purchase_price": 520000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-heart-necklace",
        "name": "گردنبند پلاک قلب نمونه",
        "category": "necklaces",
        "kind": "necklace",
        "metal": "rose",
        "description": "نمونه نمایشی. پلاک قلب برای تست کالکشن هدیه.",
        "main_price": 1080000,
        "sell_price": 980000,
        "weight": "7.40",
        "purchase_price": 450000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-chain-bracelet",
        "name": "دستبند زنجیری طلایی نمونه",
        "category": "bracelets",
        "kind": "bracelet",
        "metal": "gold",
        "description": "نمونه نمایشی. دستبند زنجیری برای تست موجودی.",
        "main_price": 970000,
        "sell_price": 870000,
        "weight": "5.80",
        "purchase_price": 400000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-woven-bangle",
        "name": "دستبند النگوی بافت نمونه",
        "category": "bracelets",
        "kind": "bracelet",
        "metal": "rose",
        "description": "نمونه نمایشی. النگوی باز برای تست صفحه دستبند.",
        "main_price": 1190000,
        "sell_price": 1090000,
        "weight": "12.50",
        "purchase_price": 510000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-thin-anklet",
        "name": "پابند زنجیر ظریف نمونه",
        "category": "anklets",
        "kind": "anklet",
        "metal": "gold",
        "description": "نمونه نمایشی. پابند سبک برای پر کردن دسته پابند.",
        "main_price": 690000,
        "sell_price": 590000,
        "weight": "3.90",
        "purchase_price": 240000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-shell-set",
        "name": "ست گردنبند و گوشواره نمونه",
        "category": "sets",
        "kind": "set",
        "metal": "gold",
        "description": "نمونه نمایشی. ست هماهنگ برای تست کالکشن هدیه.",
        "main_price": 2100000,
        "sell_price": 1890000,
        "weight": "14.80",
        "purchase_price": 890000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-men-steel-ring",
        "name": "انگشتر پهن استیل مردانه نمونه",
        "category": "men-rings",
        "kind": "ring",
        "metal": "steel",
        "description": "نمونه نمایشی. انگشتر پهن مردانه برای تست دسته مردانه.",
        "main_price": 980000,
        "sell_price": 890000,
        "weight": "8.40",
        "purchase_price": 410000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-men-signet-ring",
        "name": "انگشتر ساده مردانه نمونه",
        "category": "men-rings",
        "kind": "ring",
        "metal": "silver",
        "description": "نمونه نمایشی. انگشتر ساده نقره‌ای مردانه.",
        "main_price": 1120000,
        "sell_price": 990000,
        "weight": "9.10",
        "purchase_price": 460000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-men-chain-necklace",
        "name": "گردنبند زنجیر مردانه نمونه",
        "category": "men-necklaces",
        "kind": "necklace",
        "metal": "steel",
        "description": "نمونه نمایشی. زنجیر مردانه برای تست لیست مردانه.",
        "main_price": 1290000,
        "sell_price": 1190000,
        "weight": "16.20",
        "purchase_price": 540000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-men-thick-necklace",
        "name": "گردنبند بافت مردانه نمونه",
        "category": "men-necklaces",
        "kind": "necklace",
        "metal": "silver",
        "description": "نمونه نمایشی. زنجیر ضخیم‌تر مردانه.",
        "main_price": 1450000,
        "sell_price": 1290000,
        "weight": "18.40",
        "purchase_price": 610000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-men-chain-bracelet",
        "name": "دستبند زنجیری مردانه نمونه",
        "category": "men-bracelets",
        "kind": "bracelet",
        "metal": "steel",
        "description": "نمونه نمایشی. دستبند زنجیری مردانه.",
        "main_price": 1080000,
        "sell_price": 980000,
        "weight": "14.10",
        "purchase_price": 470000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-men-cuff",
        "name": "دستبند کاف مردانه نمونه",
        "category": "men-bracelets",
        "kind": "bracelet",
        "metal": "silver",
        "description": "نمونه نمایشی. دستبند کاف باز مردانه.",
        "main_price": 1180000,
        "sell_price": 1050000,
        "weight": "15.60",
        "purchase_price": 500000,
        "stock": 2,
    },
    {
        "slug": "maria-sample-men-hoop",
        "name": "گوشواره حلقه مردانه نمونه",
        "category": "men-earrings",
        "kind": "earrings",
        "metal": "steel",
        "description": "نمونه نمایشی. حلقه کوچک مردانه برای پر کردن دسته گوشواره.",
        "main_price": 590000,
        "sell_price": 490000,
        "weight": "1.80",
        "purchase_price": 190000,
        "stock": 2,
    },
]


class Command(BaseCommand):
    help = "Seed Maria categories, fake sample products with placeholder images, and collections."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default="fashion_jewelry_db",
        )

    def handle(self, *args, **options):
        database = options["database"]

        if database not in settings.DATABASES:
            raise CommandError(f"Unknown database: {database}")

        _tenant_local.db = database
        try:
            with transaction.atomic(using=database):
                categories = self.seed_categories(database)
                brand = self.seed_brand(database)
                products = self.seed_products(database, brand, categories)
                collections = self.seed_collections(database, products)
        finally:
            if hasattr(_tenant_local, "db"):
                del _tenant_local.db

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(categories)} categories, {len(products)} sample products, '
            f'and {len(collections)} collections into "{database}".'
        ))

    def seed_brand(self, database):
        brand, created = Brand.objects.using(database).get_or_create(
            slug="maria",
            defaults={"name": "Maria", "is_active": True},
        )
        self.stdout.write(f'Brand Maria {"created" if created else "exists"}')
        return brand

    def seed_categories(self, database):
        categories = {}

        for item in PARENT_CATEGORIES:
            category = self.upsert_category(database, item, parent=None, homepage_show=True)
            categories[item["slug"]] = category

        for item in CATEGORIES:
            parent = categories[item["parent"]]
            category = self.upsert_category(database, item, parent=parent, homepage_show=False)
            categories[item["slug"]] = category

        return categories

    def upsert_category(self, database, item, parent, homepage_show):
        defaults = {
            "name": item["name"],
            "parent": parent,
            "homepage_show": homepage_show,
            "order": item["order"],
            "seo_keywords": item["seo_keywords"],
            "seo_description": item["seo_description"],
        }
        category, created = Category.objects.using(database).get_or_create(
            slug=item["slug"],
            defaults=defaults,
        )
        if not created:
            category.name = item["name"]
            category.parent = parent
            category.homepage_show = homepage_show
            category.order = item["order"]
            category.seo_keywords = item["seo_keywords"]
            category.seo_description = item["seo_description"]
            category.save(using=database, update_fields=[
                "name", "parent", "homepage_show", "order", "seo_keywords", "seo_description", "updated_at",
            ])
        label = f"{parent.name} / {category.name}" if parent else category.name
        self.stdout.write(f'Category {label} {"created" if created else "updated"}')
        return category

    def seed_products(self, database, brand, categories):
        products = []
        for item in PRODUCTS:
            product_type, created = ProductType.objects.using(database).get_or_create(
                slug=item["slug"],
                defaults={
                    "category": categories[item["category"]],
                    "brand": brand,
                    "name": item["name"],
                    "description": item["description"],
                    "active": True,
                    "main_price": item["main_price"],
                    "sell_price": item["sell_price"],
                    "weight": item["weight"],
                    "seo_title": item["name"],
                    "seo_description": item["description"],
                    "seo_keywords": "نمونه، ماریا",
                },
            )
            products.append(product_type)

            if created:
                Product.objects.using(database).bulk_create([
                    Product(
                        product_type=product_type,
                        purchase_price=item["purchase_price"],
                        serial=f"SAMPLE-{item['slug'].upper()}-{index:02d}",
                        state=ProductState.IN_WAREHOUSE,
                    )
                    for index in range(1, item["stock"] + 1)
                ])

            if not product_type.images.using(database).exists():
                self.attach_product_images(database, product_type, item)

            self.stdout.write(f'Product {product_type.name} {"created" if created else "exists"}')

        return products

    def attach_product_images(self, database, product_type, item):
        for order, variant in enumerate(("front", "detail"), start=1):
            image = ProductImage(
                product_type=product_type,
                is_thumbnail=order == 1,
                order=order,
            )
            image.image.save(
                f"{item['slug']}-{variant}.png",
                ContentFile(render_product_image(item["kind"], item["metal"], variant)),
                save=False,
            )
            image.save(using=database)

    def seed_collections(self, database, products):
        by_slug = {product.slug: product for product in products}
        women = [product for product in products if not product.slug.startswith("maria-sample-men")]
        men = [product for product in products if product.slug.startswith("maria-sample-men")]
        gifts = [
            by_slug["maria-sample-shell-set"],
            by_slug["maria-sample-heart-necklace"],
            by_slug["maria-sample-pearl-ring"],
            by_slug["maria-sample-drop-earrings"],
        ]
        ocean = [
            by_slug["maria-sample-thin-necklace"],
            by_slug["maria-sample-thin-anklet"],
            by_slug["maria-sample-chain-bracelet"],
            by_slug["maria-sample-star-earrings"],
            by_slug["maria-sample-men-chain-necklace"],
        ]

        specs = [
            {
                "code_name": "new-arrivals",
                "name": "جدیدترین‌ها",
                "caption": "New arrivals",
                "order": 10,
                "description": "نمونه‌های نمایشی برای تست صفحه اصلی.",
                "products": products,
                "metal": "gold",
            },
            {
                "code_name": "for-her",
                "name": "انتخاب زنانه",
                "caption": "For her",
                "order": 20,
                "description": "همه نمونه‌های زنانه برای تست دسته زنانه.",
                "products": women,
                "metal": "rose",
            },
            {
                "code_name": "for-him",
                "name": "انتخاب مردانه",
                "caption": "For him",
                "order": 30,
                "description": "همه نمونه‌های مردانه برای تست دسته مردانه.",
                "products": men,
                "metal": "steel",
            },
            {
                "code_name": "gifts",
                "name": "مناسب هدیه",
                "caption": "Gifts",
                "order": 40,
                "description": "ست و قطعات مناسب هدیه برای تست کالکشن.",
                "products": gifts,
                "metal": "gold",
            },
            {
                "code_name": "ocean",
                "name": "کالکشن دریا",
                "caption": "Ocean",
                "order": 50,
                "description": "انتخاب با حس برند ماریا برای تست کالکشن اختصاصی.",
                "products": ocean,
                "metal": "silver",
            },
        ]

        collections = []
        for spec in specs:
            collection, created = ProductCollection.objects.using(database).get_or_create(
                code_name=spec["code_name"],
                defaults={
                    "name": spec["name"],
                    "is_active": True,
                    "order": spec["order"],
                    "description": spec["description"],
                    "seo_title": spec["name"],
                    "seo_description": spec["description"],
                },
            )
            if not collection.image:
                collection.image.save(
                    f"{spec['code_name']}.png",
                    ContentFile(render_collection_image(spec["caption"], spec["metal"])),
                    save=False,
                )
                collection.save(using=database)
            collection.product_types.set(spec["products"])
            collections.append(collection)
            self.stdout.write(f'Collection {collection.name} {"created" if created else "updated"}')

        return collections


def load_font(size):
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size)
    return ImageFont.load_default()


def render_product_image(kind, metal, variant):
    size = 1600
    image = Image.new("RGB", (size, size), (247, 245, 242))
    draw = ImageDraw.Draw(image)
    color = METALS[metal]
    shadow = (90, 98, 102)

    draw.ellipse((180, 180, 1420, 1420), fill=(232, 241, 245))
    if variant == "detail":
        draw.ellipse((420, 260, 1280, 1120), fill=(232, 226, 218))

    draw_jewelry(draw, kind, color, shadow, variant)

    image = image.filter(ImageFilter.SMOOTH)
    image = image.resize((800, 800), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(image)
    draw.text((40, 720), "MARIA  SAMPLE", font=load_font(28), fill=(10, 77, 110))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def draw_jewelry(draw, kind, color, shadow, variant):
    offset = 18 if variant == "front" else 0

    if kind == "ring":
        box = (480 + offset, 480, 1120 + offset, 1120)
        draw.ellipse(box, outline=shadow, width=70)
        draw.ellipse(box, outline=color, width=46)
        draw.ellipse((680 + offset, 680, 920 + offset, 920), fill=(247, 245, 242))
        if variant == "detail":
            draw.ellipse((760 + offset, 430, 860 + offset, 530), fill=color)
        return

    if kind == "earrings":
        for left in (430, 860):
            draw.ellipse((left + 90 + offset, 320, left + 170 + offset, 400), outline=color, width=16)
            draw.polygon(
                [
                    (left + 40 + offset, 520),
                    (left + 220 + offset, 520),
                    (left + 130 + offset, 980),
                ],
                fill=color,
            )
            draw.ellipse((left + 70 + offset, 560, left + 190 + offset, 780), fill=shadow)
        return

    if kind == "necklace":
        draw.arc((280 + offset, 260, 1320 + offset, 1100), start=20, end=160, fill=color, width=18)
        draw.polygon(
            [
                (720 + offset, 820),
                (880 + offset, 820),
                (800 + offset, 1080),
            ],
            fill=color,
        )
        return

    if kind in {"bracelet", "anklet"}:
        width = 36 if kind == "bracelet" else 20
        box = (300 + offset, 520, 1300 + offset, 1080)
        draw.ellipse(box, outline=shadow, width=width + 18)
        draw.ellipse(box, outline=color, width=width)
        return

    draw.arc((360 + offset, 240, 1240 + offset, 900), start=25, end=155, fill=color, width=16)
    draw.ellipse((720 + offset, 860, 880 + offset, 1020), fill=color)
    draw.polygon(
        [(480 + offset, 1100), (620 + offset, 1100), (550 + offset, 1320)],
        fill=color,
    )
    draw.polygon(
        [(980 + offset, 1100), (1120 + offset, 1100), (1050 + offset, 1320)],
        fill=color,
    )


def render_collection_image(title, metal):
    image = Image.new("RGB", (1400, 700), (10, 77, 110))
    draw = ImageDraw.Draw(image)
    color = METALS[metal]
    draw.ellipse((820, -80, 1580, 620), fill=(21, 101, 140))
    draw.ellipse((980, 180, 1360, 560), outline=color, width=18)
    draw.text((80, 220), "MARIA", font=load_font(72), fill=(247, 245, 242))
    draw.text((80, 330), title, font=load_font(44), fill=color)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from config.middleware import _tenant_local
from product.models import Category


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


class Command(BaseCommand):
    help = "Seed Maria fashion jewelry categories only. Products are added later with images."

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
        finally:
            if hasattr(_tenant_local, "db"):
                del _tenant_local.db

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(categories)} categories into "{database}".'
        ))

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

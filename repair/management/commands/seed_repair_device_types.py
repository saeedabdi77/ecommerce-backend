from django.core.management.base import BaseCommand, CommandError

from repair.models import RepairDeviceType


DEVICE_TYPES = [
    # =========================
    # PlayStation Consoles
    # =========================
    "PlayStation",
    "PlayStation 2",
    "PlayStation 2 Slim",
    "PlayStation 3",
    "PlayStation 3 Slim",
    "PlayStation 3 Super Slim",
    "PlayStation 4",
    "PlayStation 4 Slim",
    "PlayStation 4 Pro",
    "PlayStation 5",
    "PlayStation 5 Slim",
    "PlayStation 5 Pro",

    # =========================
    # PlayStation Controllers
    # =========================
    "PlayStation Controller",
    "DualShock",
    "DualShock 2",
    "DualShock 3",
    "DualShock 4",
    "DualSense",
    "DualSense Edge",

    # =========================
    # Xbox Consoles
    # =========================
    "Xbox",
    "Xbox 360",
    "Xbox 360 Slim",
    "Xbox 360 E",
    "Xbox One",
    "Xbox One S",
    "Xbox One X",
    "Xbox Series S",
    "Xbox Series X",

    # =========================
    # Xbox Controllers
    # =========================
    "Xbox Controller",
    "Xbox 360 Controller",
    "Xbox One Controller",
    "Xbox Wireless Controller",
    "Xbox Elite Controller",
    "Xbox Elite Wireless Controller Series 2",

    # =========================
    # Nintendo Consoles
    # =========================
    "Nintendo Entertainment System",
    "Super Nintendo Entertainment System",
    "Nintendo 64",
    "Nintendo GameCube",
    "Nintendo Wii",
    "Nintendo Wii U",
    "Nintendo Switch",
    "Nintendo Switch Lite",
    "Nintendo Switch OLED",
    "Nintendo Switch 2",

    # =========================
    # Nintendo Controllers
    # =========================
    "Nintendo Controller",
    "Nintendo 64 Controller",
    "GameCube Controller",
    "Wii Remote",
    "Wii U GamePad",
    "Wii U Pro Controller",
    "Joy-Con",
    "Nintendo Switch Pro Controller",
    "Nintendo Switch 2 Joy-Con",
    "Nintendo Switch 2 Pro Controller",

    # =========================
    # Steam / PC Gaming
    # =========================
    "Steam Deck",
    "Steam Deck LCD",
    "Steam Deck OLED",
    "Steam Controller",

    # =========================
    # Other Consoles
    # =========================
    "Sega Genesis",
    "Sega Mega Drive",
    "Sega Saturn",
    "Sega Dreamcast",
    "Atari 2600",
    "Atari 5200",
    "Atari 7800",
    "Atari Jaguar",

    # =========================
    # Handheld Consoles
    # =========================
    "PlayStation Portable",
    "PSP",
    "PlayStation Vita",
    "PS Vita",
    "Nintendo DS",
    "Nintendo DS Lite",
    "Nintendo DSi",
    "Nintendo 3DS",
    "Nintendo 3DS XL",
    "Nintendo 2DS",
    "New Nintendo 3DS",
    "New Nintendo 3DS XL",

    # =========================
    # Handheld Controllers
    # =========================
    "PSP Controller",
    "PS Vita Controller",
    "Nintendo DS Controller",
    "Nintendo 3DS Controller",
]


class Command(BaseCommand):
    help = "Seed repair device types into the selected database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            required=True,
            help="Database alias to insert the device types into.",
        )

    def handle(self, *args, **options):
        database = options["database"]

        if database not in self.get_database_aliases():
            raise CommandError(
                f"Unknown database '{database}'. "
                f"Available databases: {', '.join(self.get_database_aliases())}"
            )

        created_count = 0
        existing_count = 0

        for name in DEVICE_TYPES:
            _, created = RepairDeviceType.objects.using(database).get_or_create(
                name=name,
                defaults={
                    "active": True,
                    "order": 10,
                },
            )

            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded repair device types into '{database}'."
            )
        )

        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Already existed: {existing_count}")
        self.stdout.write(f"Total in dataset: {len(DEVICE_TYPES)}")

    @staticmethod
    def get_database_aliases():
        from django.conf import settings

        return list(settings.DATABASES.keys())

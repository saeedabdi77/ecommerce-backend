import os
import re
from urllib.parse import urlparse

import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from installation.models import (
    Game,
    GameRate,
    GameRateSource,
    InstallationDeviceType,
)


API_URL = "https://api.thegamesdb.net/v1"
TIMEOUT = 30

DEVICES = {
    "PlayStation 4": 4916,
    "PlayStation 5": 4980,
    "Xbox One": 4920,
    "Xbox Series X": 5000,
    "Xbox Series S": 5000,
    "Nintendo Switch": 4971,
}

GAMES = [
    "Grand Theft Auto V",
    "Grand Theft Auto VI",
    "Red Dead Redemption 2",
    "Red Dead Redemption",
    "The Last of Us Part I",
    "The Last of Us Part II",
    "God of War",
    "God of War Ragnarök",
    "Marvel's Spider-Man",
    "Marvel's Spider-Man 2",
    "Marvel's Spider-Man: Miles Morales",
    "Ghost of Tsushima",
    "Horizon Zero Dawn",
    "Horizon Forbidden West",
    "Uncharted 4: A Thief's End",
    "Uncharted: The Lost Legacy",
    "Days Gone",
    "Bloodborne",
    "Demon's Souls",
    "Elden Ring",
    "Dark Souls Remastered",
    "Dark Souls II",
    "Dark Souls III",
    "Sekiro: Shadows Die Twice",
    "Lies of P",
    "Cyberpunk 2077",
    "The Witcher 3: Wild Hunt",
    "Hogwarts Legacy",
    "Assassin's Creed Valhalla",
    "Assassin's Creed Odyssey",
    "Assassin's Creed Origins",
    "Assassin's Creed Mirage",
    "Far Cry 5",
    "Far Cry 6",
    "Resident Evil 2",
    "Resident Evil 3",
    "Resident Evil 4",
    "Resident Evil 7: Biohazard",
    "Resident Evil Village",
    "Resident Evil 5",
    "Resident Evil 6",
    "Mortal Kombat 11",
    "Mortal Kombat 1",
    "Tekken 7",
    "Tekken 8",
    "Street Fighter V",
    "Street Fighter 6",
    "EA Sports FC 24",
    "EA Sports FC 25",
    "EA Sports FC 26",
    "FIFA 23",
    "Call of Duty: Modern Warfare",
    "Call of Duty: Modern Warfare II",
    "Call of Duty: Modern Warfare III",
    "Call of Duty: Black Ops III",
    "Call of Duty: Black Ops Cold War",
    "Call of Duty: Black Ops 6",
    "Call of Duty: Black Ops 7",
    "Call of Duty: Vanguard",
    "Battlefield 1",
    "Battlefield V",
    "Battlefield 2042",
    "Far Cry 4",
    "Dying Light",
    "Dying Light 2",
    "Dead Space",
    "Dead Space 2",
    "Dead Space 3",
    "Alan Wake Remastered",
    "Alan Wake 2",
    "Control",
    "Death Stranding",
    "Death Stranding 2",
    "Metal Gear Solid V: The Phantom Pain",
    "Metal Gear Solid Delta: Snake Eater",
    "Final Fantasy VII Remake",
    "Final Fantasy VII Rebirth",
    "Final Fantasy XVI",
    "Final Fantasy XV",
    "Kingdom Hearts III",
    "Dragon Ball Z: Kakarot",
    "Dragon Ball: Sparking! ZERO",
    "Demon Slayer -Kimetsu no Yaiba- The Hinokami Chronicles",
    "Monster Hunter: World",
    "Monster Hunter Rise",
    "Monster Hunter Wilds",
    "Black Myth: Wukong",
    "Stellar Blade",
    "Armored Core VI: Fires of Rubicon",
    "Helldivers 2",
    "Returnal",
    "Ratchet & Clank: Rift Apart",
    "Gran Turismo 7",
    "The Crew Motorfest",
    "Need for Speed Heat",
    "Need for Speed Unbound",
    "Forza Horizon 4",
    "Forza Horizon 5",
    "Forza Motorsport",
    "Halo Infinite",
    "Halo 5: Guardians",
    "Gears 5",
    "Sea of Thieves",
    "Starfield",
    "The Elder Scrolls V: Skyrim",
    "Fallout 4",
    "Fallout 76",
    "Doom",
    "Doom Eternal",
    "Wolfenstein II: The New Colossus",
    "Minecraft",
    "Terraria",
    "Cyberpunk 2077",
    "Baldur's Gate 3",
    "Divinity: Original Sin 2",
    "Diablo IV",
    "Overwatch 2",
    "Fortnite",
    "Apex Legends",
    "Rocket League",
    "Mortal Kombat X",
    "Injustice 2",
    "WWE 2K24",
    "WWE 2K25",
    "NBA 2K24",
    "NBA 2K25",
    "NBA 2K26",
    "Tekken 8",
    "The Crew 2",
    "Watch Dogs",
    "Watch Dogs 2",
    "Watch Dogs: Legion",
    "Sleeping Dogs",
    "Hitman",
    "Hitman 2",
    "Hitman 3",
    "Hitman: World of Assassination",
    "Just Cause 3",
    "Just Cause 4",
    "Tomb Raider",
    "Rise of the Tomb Raider",
    "Shadow of the Tomb Raider",
    "Lara Croft and the Temple of Osiris",
    "Kingdom Come: Deliverance",
    "Kingdom Come: Deliverance II",
    "Dragon Age: Inquisition",
    "Dragon Age: The Veilguard",
    "Mass Effect Legendary Edition",
    "Star Wars Jedi: Fallen Order",
    "Star Wars Jedi: Survivor",
    "Star Wars Outlaws",
    "Avatar: Frontiers of Pandora",
    "Prince of Persia: The Lost Crown",
    "Sonic Frontiers",
    "Sonic Superstars",
    "Crash Bandicoot N. Sane Trilogy",
    "Crash Bandicoot 4: It's About Time",
    "Spyro Reignited Trilogy",
    "Tony Hawk's Pro Skater 1 + 2",
    "Little Nightmares",
    "Little Nightmares II",
    "It Takes Two",
    "A Way Out",
    "Stray",
    "Kena: Bridge of Spirits",
    "Sackboy: A Big Adventure",
    "Lego Star Wars: The Skywalker Saga",
    "Lego Harry Potter Collection",
    "Teenage Mutant Ninja Turtles: Shredder's Revenge",
    "Cuphead",
    "Hades",
    "Hades II",
    "Hollow Knight",
    "Ori and the Blind Forest",
    "Ori and the Will of the Wisps",
    "Subnautica",
    "Subnautica: Below Zero",
    "No Man's Sky",
    "The Outer Worlds",
    "Outer Wilds",
    "Borderlands 3",
    "Tiny Tina's Wonderlands",
    "Destiny 2",
    "Warframe",
    "Resident Evil 4",
    "Silent Hill 2",
    "Dead by Daylight",
    "The Quarry",
    "Until Dawn",
    "A Plague Tale: Innocence",
    "A Plague Tale: Requiem",
    "Ghostrunner",
    "Ghostrunner 2",
    "Remnant: From the Ashes",
    "Remnant II",
    "Payday 2",
    "Payday 3",
    "The Division",
    "The Division 2",
    "Tom Clancy's Rainbow Six Siege",
    "Tom Clancy's Ghost Recon Wildlands",
    "Tom Clancy's Ghost Recon Breakpoint",
    "Mafia: Definitive Edition",
    "Mafia II: Definitive Edition",
    "Mafia III",
    "L.A. Noire",
    "Bully",
    "Grand Theft Auto: San Andreas",
    "Grand Theft Auto: Vice City",
    "Grand Theft Auto III",
    "Grand Theft Auto IV",
    "Red Dead Redemption",
]


class Command(BaseCommand):
    help = "Seed popular console games from TheGamesDB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            required=True,
        )
        parser.add_argument(
            "--api-key",
            default=None,
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
        )

    def handle(self, *args, **options):
        database = options["database"]
        api_key = options["api_key"] or os.getenv("TGDB_API_KEY")
        limit = options["limit"]

        if database not in settings.DATABASES:
            raise CommandError(
                f"Unknown database: {database}"
            )

        if not api_key:
            raise CommandError(
                "TGDB_API_KEY is not configured."
            )

        games = GAMES[:limit] if limit else GAMES

        devices = self.seed_devices(database)

        session = requests.Session()

        created = 0
        skipped = 0

        for name in games:
            result = self.import_game(
                database=database,
                name=name,
                api_key=api_key,
                devices=devices,
                session=session,
            )

            if result:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {name}"
                    )
                )
            else:
                skipped += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, skipped: {skipped}"
            )
        )

    def seed_devices(self, database):
        devices = {}

        for order, name in enumerate(DEVICES, start=1):
            device, _ = (
                InstallationDeviceType.objects
                .using(database)
                .get_or_create(
                    name=name,
                    defaults={
                        "active": True,
                        "order": order * 10,
                    },
                )
            )

            devices[name] = device

        return devices

    def import_game(
        self,
        *,
        database,
        name,
        api_key,
        devices,
        session,
    ):
        if (
            Game.objects
            .using(database)
            .filter(name__iexact=name)
            .exists()
        ):
            return False

        data = self.search_game(
            session=session,
            api_key=api_key,
            name=name,
        )

        if not data:
            return False

        game_data = data[0]

        game = Game(
            name=game_data.get("game_title") or name,
            size=0,
            price=0,
            active=True,
        )

        image_url = self.get_image_url(game_data)

        if image_url:
            image = self.download_image(
                session,
                image_url,
            )

            if image:
                game.image.save(
                    self.image_name(
                        game.name,
                        image_url,
                    ),
                    ContentFile(image),
                    save=False,
                )

        game.save(using=database)

        platform_names = self.get_platforms(game_data)

        game.device_type.set(
            [
                devices[platform]
                for platform in platform_names
                if platform in devices
            ]
        )

        self.create_rate(
            database=database,
            game=game,
            data=game_data,
        )

        return True

    def search_game(
        self,
        *,
        session,
        api_key,
        name,
    ):
        response = session.get(
            f"{API_URL}/Games/ByGameName",
            params={
                "apikey": api_key,
                "name": name,
            },
            timeout=TIMEOUT,
        )

        if not response.ok:
            self.stdout.write(
                self.style.WARNING(
                    f"API error for {name}: "
                    f"HTTP {response.status_code}"
                )
            )
            return []

        try:
            data = response.json()
        except ValueError:
            return []

        if data.get("code") != 200:
            return []

        return data.get("data", {}).get("games", [])

    @staticmethod
    def get_platforms(data):
        result = set()

        platforms = data.get("platforms") or []

        if isinstance(platforms, dict):
            platforms = platforms.values()

        for platform in platforms:
            name = str(
                platform.get("name", "")
            ).lower()

            if "playstation 4" in name:
                result.add("PlayStation 4")

            elif "playstation 5" in name:
                result.add("PlayStation 5")

            elif "xbox one" in name:
                result.add("Xbox One")

            elif "xbox series" in name:
                result.add("Xbox Series X")
                result.add("Xbox Series S")

            elif "nintendo switch" in name:
                result.add("Nintendo Switch")

        return result

    @staticmethod
    def get_image_url(data):
        images = data.get("images")

        if not images:
            return None

        if isinstance(images, dict):
            images = images.get("boxart") or images.get(
                "fanart"
            )

        if isinstance(images, list) and images:
            image = images[0]

            if isinstance(image, str):
                return image

            return (
                image.get("original")
                or image.get("thumb")
                or image.get("url")
            )

        return None

    @staticmethod
    def create_rate(*, database, game, data):
        rating = data.get("rating")

        if rating is None:
            return

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return

        if rating > 10:
            rating = rating / 10

        GameRate.objects.using(database).get_or_create(
            game=game,
            source=GameRateSource.METACRITIC,
            defaults={
                "rate": round(rating, 1),
            },
        )

    @staticmethod
    def download_image(session, url):
        try:
            response = session.get(
                url,
                timeout=TIMEOUT,
            )
        except requests.RequestException:
            return None

        if not response.ok:
            return None

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        if not content_type.startswith("image/"):
            return None

        return response.content

    @staticmethod
    def image_name(name, url):
        extension = os.path.splitext(
            urlparse(url).path
        )[1].lower()

        if extension not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            extension = ".jpg"

        slug = re.sub(
            r"[^a-zA-Z0-9]+",
            "-",
            name.lower(),
        ).strip("-")

        return f"{slug or 'game'}{extension}"

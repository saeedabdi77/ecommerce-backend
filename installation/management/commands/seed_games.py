import os

import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from installation.models import InstallationDeviceType, Game


API_URL = "https://api.thegamesdb.net/v1"
TIMEOUT = 30


DEVICE_TYPES = {
    "PlayStation 5": [
        "PlayStation 5",
    ],
    "PlayStation 4": [
        "PlayStation 4",
    ],
    "Xbox Series X/S": [
        "Xbox Series X",
        "Xbox Series S",
        "Xbox Series X/S",
    ],
    "Xbox One": [
        "Xbox One",
    ],
    "Nintendo Switch": [
        "Nintendo Switch",
    ],
}


GAMES = [
    ("Grand Theft Auto VI", ["PlayStation 5", "Xbox Series X/S"]),
    ("Red Dead Redemption 2", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Red Dead Redemption", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("The Last of Us Part I", ["PlayStation 5"]),
    ("The Last of Us Part II", ["PlayStation 5", "PlayStation 4"]),
    ("God of War", ["PlayStation 5", "PlayStation 4"]),
    ("God of War Ragnarök", ["PlayStation 5", "PlayStation 4"]),
    ("Marvel's Spider-Man", ["PlayStation 5", "PlayStation 4"]),
    ("Marvel's Spider-Man 2", ["PlayStation 5"]),
    ("Marvel's Spider-Man: Miles Morales", ["PlayStation 5", "PlayStation 4"]),
    ("Ghost of Tsushima", ["PlayStation 5", "PlayStation 4"]),
    ("Horizon Zero Dawn", ["PlayStation 5", "PlayStation 4"]),
    ("Horizon Forbidden West", ["PlayStation 5", "PlayStation 4"]),
    ("Uncharted 4: A Thief's End", ["PlayStation 5", "PlayStation 4"]),
    ("Uncharted: The Lost Legacy", ["PlayStation 5", "PlayStation 4"]),
    ("Days Gone", ["PlayStation 5", "PlayStation 4"]),
    ("Bloodborne", ["PlayStation 4"]),
    ("Demon's Souls", ["PlayStation 5"]),
    ("Elden Ring", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Dark Souls Remastered", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Dark Souls II", ["PlayStation 4", "Xbox One"]),
    ("Dark Souls III", ["PlayStation 4", "Xbox One"]),
    ("Sekiro: Shadows Die Twice", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Lies of P", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Cyberpunk 2077", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("The Witcher 3: Wild Hunt", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Hogwarts Legacy", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Assassin's Creed Valhalla", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Assassin's Creed Odyssey", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Assassin's Creed Origins", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Assassin's Creed Mirage", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Far Cry 5", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Far Cry 6", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Resident Evil 2", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Resident Evil 3", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Resident Evil 4", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Resident Evil 7: Biohazard", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Resident Evil Village", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Resident Evil 5", ["PlayStation 4", "Xbox One"]),
    ("Resident Evil 6", ["PlayStation 4", "Xbox One"]),
    ("Mortal Kombat 11", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Mortal Kombat 1", ["PlayStation 5", "Xbox Series X/S", "Nintendo Switch"]),
    ("Tekken 7", ["PlayStation 4", "Xbox One"]),
    ("Tekken 8", ["PlayStation 5", "Xbox Series X/S"]),
    ("Street Fighter V", ["PlayStation 4"]),
    ("Street Fighter 6", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S"]),
    ("EA Sports FC 24", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("EA Sports FC 25", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("EA Sports FC 26", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("FIFA 23", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Call of Duty: Modern Warfare", ["PlayStation 4", "Xbox One"]),
    ("Call of Duty: Modern Warfare II", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Call of Duty: Modern Warfare III", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Call of Duty: Black Ops III", ["PlayStation 4", "Xbox One"]),
    ("Call of Duty: Black Ops Cold War", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Call of Duty: Black Ops 6", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Call of Duty: Black Ops 7", ["PlayStation 5", "Xbox Series X/S"]),
    ("Call of Duty: Vanguard", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Battlefield 1", ["PlayStation 4", "Xbox One"]),
    ("Battlefield V", ["PlayStation 4", "Xbox One"]),
    ("Battlefield 2042", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Dying Light", ["PlayStation 4", "Xbox One"]),
    ("Dying Light 2", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Dead Space", ["PlayStation 5", "Xbox Series X/S"]),
    ("Dead Space 2", ["PlayStation 4", "Xbox One"]),
    ("Dead Space 3", ["PlayStation 4", "Xbox One"]),
    ("Alan Wake Remastered", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Alan Wake 2", ["PlayStation 5", "Xbox Series X/S"]),
    ("Control", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Death Stranding", ["PlayStation 5", "PlayStation 4"]),
    ("Death Stranding 2", ["PlayStation 5"]),
    ("Metal Gear Solid V: The Phantom Pain", ["PlayStation 4", "Xbox One"]),
    ("Metal Gear Solid Delta: Snake Eater", ["PlayStation 5", "Xbox Series X/S"]),
    ("Final Fantasy VII Remake", ["PlayStation 5", "PlayStation 4"]),
    ("Final Fantasy VII Rebirth", ["PlayStation 5"]),
    ("Final Fantasy XVI", ["PlayStation 5"]),
    ("Final Fantasy XV", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Kingdom Hearts III", ["PlayStation 4", "Xbox One"]),
    ("Dragon Ball Z: Kakarot", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Dragon Ball: Sparking! ZERO", ["PlayStation 5", "Xbox Series X/S"]),
    ("Monster Hunter: World", ["PlayStation 4", "Xbox One"]),
    ("Monster Hunter Rise", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Monster Hunter Wilds", ["PlayStation 5", "Xbox Series X/S"]),
    ("Black Myth: Wukong", ["PlayStation 5", "Xbox Series X/S"]),
    ("Stellar Blade", ["PlayStation 5"]),
    ("Armored Core VI: Fires of Rubicon", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Helldivers 2", ["PlayStation 5"]),
    ("Returnal", ["PlayStation 5"]),
    ("Ratchet & Clank: Rift Apart", ["PlayStation 5"]),
    ("Gran Turismo 7", ["PlayStation 5", "PlayStation 4"]),
    ("The Crew Motorfest", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Need for Speed Heat", ["PlayStation 4", "Xbox One"]),
    ("Need for Speed Unbound", ["PlayStation 5", "Xbox Series X/S"]),
    ("Forza Horizon 4", ["Xbox One"]),
    ("Forza Horizon 5", ["Xbox Series X/S", "Xbox One"]),
    ("Forza Motorsport", ["Xbox Series X/S"]),
    ("Halo Infinite", ["Xbox Series X/S", "Xbox One"]),
    ("Halo 5: Guardians", ["Xbox One"]),
    ("Gears 5", ["Xbox One"]),
    ("Sea of Thieves", ["Xbox Series X/S", "Xbox One"]),
    ("Starfield", ["Xbox Series X/S"]),
    ("The Elder Scrolls V: Skyrim", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Fallout 4", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("Fallout 76", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Doom", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Doom Eternal", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Minecraft", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Terraria", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Baldur's Gate 3", ["PlayStation 5", "Xbox Series X/S"]),
    ("Divinity: Original Sin 2", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Diablo IV", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Overwatch 2", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Fortnite", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Apex Legends", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Rocket League", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Mortal Kombat X", ["PlayStation 4", "Xbox One"]),
    ("Injustice 2", ["PlayStation 4", "Xbox One"]),
    ("WWE 2K24", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("WWE 2K25", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("NBA 2K24", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("NBA 2K25", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("NBA 2K26", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("The Crew 2", ["PlayStation 4", "Xbox One"]),
    ("Watch Dogs", ["PlayStation 4", "Xbox One"]),
    ("Watch Dogs 2", ["PlayStation 4", "Xbox One"]),
    ("Watch Dogs: Legion", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Sleeping Dogs", ["PlayStation 4", "Xbox One"]),
    ("Hitman", ["PlayStation 4", "Xbox One"]),
    ("Hitman 2", ["PlayStation 4", "Xbox One"]),
    ("Hitman 3", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Just Cause 3", ["PlayStation 4", "Xbox One"]),
    ("Just Cause 4", ["PlayStation 4", "Xbox One"]),
    ("Tomb Raider", ["PlayStation 4", "Xbox One"]),
    ("Rise of the Tomb Raider", ["PlayStation 4", "Xbox One"]),
    ("Shadow of the Tomb Raider", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Kingdom Come: Deliverance", ["PlayStation 4", "Xbox One"]),
    ("Kingdom Come: Deliverance II", ["PlayStation 5", "Xbox Series X/S"]),
    ("Dragon Age: Inquisition", ["PlayStation 4", "Xbox One"]),
    ("Dragon Age: The Veilguard", ["PlayStation 5", "Xbox Series X/S"]),
    ("Mass Effect Legendary Edition", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Star Wars Jedi: Fallen Order", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Star Wars Jedi: Survivor", ["PlayStation 5", "Xbox Series X/S"]),
    ("Star Wars Outlaws", ["PlayStation 5", "Xbox Series X/S"]),
    ("Avatar: Frontiers of Pandora", ["PlayStation 5", "Xbox Series X/S"]),
    ("Prince of Persia: The Lost Crown", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Sonic Frontiers", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Sonic Superstars", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Crash Bandicoot N. Sane Trilogy", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Crash Bandicoot 4: It's About Time", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Spyro Reignited Trilogy", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Tony Hawk's Pro Skater 1 + 2", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Little Nightmares", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Little Nightmares II", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("It Takes Two", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("A Way Out", ["PlayStation 4", "Xbox One"]),
    ("Stray", ["PlayStation 5", "PlayStation 4"]),
    ("Kena: Bridge of Spirits", ["PlayStation 5", "PlayStation 4"]),
    ("Sackboy: A Big Adventure", ["PlayStation 5", "PlayStation 4"]),
    ("Cuphead", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Hades", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Hades II", ["Nintendo Switch"]),
    ("Hollow Knight", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Ori and the Blind Forest", ["Xbox One", "Nintendo Switch"]),
    ("Ori and the Will of the Wisps", ["Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Subnautica", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Subnautica: Below Zero", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("No Man's Sky", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("The Outer Worlds", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Outer Wilds", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Borderlands 3", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Tiny Tina's Wonderlands", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Destiny 2", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Warframe", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Silent Hill 2", ["PlayStation 5"]),
    ("Dead by Daylight", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("The Quarry", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Until Dawn", ["PlayStation 5"]),
    ("A Plague Tale: Innocence", ["PlayStation 5", "PlayStation 4", "Xbox One"]),
    ("A Plague Tale: Requiem", ["PlayStation 5", "Xbox Series X/S"]),
    ("Ghostrunner", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One", "Nintendo Switch"]),
    ("Ghostrunner 2", ["PlayStation 5", "Xbox Series X/S"]),
    ("Remnant: From the Ashes", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Remnant II", ["PlayStation 5", "Xbox Series X/S"]),
    ("Payday 2", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Payday 3", ["PlayStation 5", "Xbox Series X/S"]),
    ("The Division", ["PlayStation 4", "Xbox One"]),
    ("The Division 2", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Tom Clancy's Rainbow Six Siege", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Tom Clancy's Ghost Recon Wildlands", ["PlayStation 4", "Xbox One"]),
    ("Tom Clancy's Ghost Recon Breakpoint", ["PlayStation 5", "PlayStation 4", "Xbox Series X/S", "Xbox One"]),
    ("Mafia: Definitive Edition", ["PlayStation 4", "Xbox One"]),
    ("Mafia II: Definitive Edition", ["PlayStation 4", "Xbox One"]),
    ("Mafia III", ["PlayStation 4", "Xbox One"]),
    ("L.A. Noire", ["PlayStation 4", "Xbox One", "Nintendo Switch"]),
    ("Bully", ["PlayStation 4", "Xbox One"]),
    ("Grand Theft Auto: San Andreas", ["PlayStation 4", "Xbox One"]),
    ("Grand Theft Auto: Vice City", ["PlayStation 4", "Xbox One"]),
    ("Grand Theft Auto III", ["PlayStation 4", "Xbox One"]),
    ("Grand Theft Auto IV", ["Xbox One"]),
]


class Command(BaseCommand):
    help = "Seed installation games with TheGamesDB images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            required=True,
        )
        parser.add_argument(
            "--api-key",
            default=None,
        )

    def handle(self, *args, **options):
        database = options["database"]
        api_key = options["api_key"] or os.getenv("TGDB_API_KEY")

        if database not in settings.DATABASES:
            raise CommandError(f"Unknown database: {database}")

        if not api_key:
            raise CommandError("TGDB_API_KEY is not configured.")

        session = requests.Session()

        devices = self.seed_devices(database)

        created = 0
        skipped = 0
        images = 0
        no_images = []

        for name, device_names in GAMES:
            if Game.objects.using(database).filter(name=name).exists():
                skipped += 1
                continue

            game_data = self.find_game(
                name=name,
                api_key=api_key,
                session=session,
            )

            if not game_data:
                self.stdout.write(
                    self.style.WARNING(
                        f"Not found: {name}"
                    )
                )
                skipped += 1
                continue

            game = Game(
                name=name,
                size=0,
                price=0,
                active=True,
            )

            image = self.download_image(
                game_data=game_data,
                api_key=api_key,
                session=session,
            )

            if image:
                game.image.save(
                    image["name"],
                    ContentFile(image["content"]),
                    save=False,
                )
                images += 1
            else:
                no_images.append(name)

            game.save(using=database)

            game.device_type.set(
                [
                    devices[device_name]
                    for device_name in device_names
                    if device_name in devices
                ]
            )

            created += 1

            if image:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {name} [image]"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Created: {name} [no image]"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created}, "
                f"skipped: {skipped}, "
                f"images: {images}"
            )
        )

        if no_images:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("Games without images:")
            )

            for name in no_images:
                self.stdout.write(f"- {name}")

    def seed_devices(self, database):
        devices = {}

        for order, name in enumerate(DEVICE_TYPES, start=1):
            device, _ = InstallationDeviceType.objects.using(
                database
            ).get_or_create(
                name=name,
                defaults={
                    "active": True,
                    "order": order,
                },
            )

            devices[name] = device

        return devices

    @staticmethod
    def find_game(name, api_key, session):
        try:
            response = session.get(
                f"{API_URL}/Games/ByGameName",
                params={
                    "apikey": api_key,
                    "name": name,
                },
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            return None

        games = (
            data
            .get("data", {})
            .get("games", [])
        )

        if not games:
            return None

        return games[0]

    @staticmethod
    def download_image(game_data, api_key, session):
        game_id = game_data.get("id")

        if not game_id:
            return None

        try:
            response = session.get(
                f"{API_URL}/Games/Images",
                params={
                    "apikey": api_key,
                    "games_id": game_id,
                },
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError):
            return None

        image_data = data.get("data", {})

        base_url = (
            image_data
            .get("base_url", {})
            .get("original")
        )

        images = image_data.get("images", {})

        if not base_url or not isinstance(images, dict):
            return None

        game_images = images.get(str(game_id), [])

        if not isinstance(game_images, list):
            return None

        boxart = next(
            (
                image
                for image in game_images
                if isinstance(image, dict)
                and image.get("type") == "boxart"
                and image.get("side") == "front"
                and image.get("filename")
            ),
            None,
        )

        if not boxart:
            return None

        filename = boxart["filename"]

        try:
            response = session.get(
                f"{base_url}{filename}",
                timeout=TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException:
            return None

        return {
            "name": os.path.basename(filename),
            "content": response.content,
        }

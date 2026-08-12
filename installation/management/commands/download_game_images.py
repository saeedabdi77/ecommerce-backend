import os

import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from installation.models import Game


API_URL = "https://api.thegamesdb.net/v1/Games/Images"
TIMEOUT = 30


class Command(BaseCommand):
    help = "Download missing game images from TheGamesDB."

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
            raise CommandError(
                f"Unknown database: {database}"
            )

        if not api_key:
            raise CommandError(
                "TGDB_API_KEY is not configured."
            )

        games = (
            Game.objects
            .using(database)
            .filter(image="")
        )

        total = games.count()

        self.stdout.write(
            f"Games without images: {total}"
        )

        session = requests.Session()

        downloaded = 0
        skipped = 0

        for game in games.iterator():
            success = self.download_image(
                game=game,
                database=database,
                api_key=api_key,
                session=session,
            )

            if success:
                downloaded += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Downloaded: {game.name}"
                    )
                )
            else:
                skipped += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped: {game.name}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Downloaded: {downloaded}, "
                f"skipped: {skipped}"
            )
        )

    def download_image(
        self,
        *,
        game,
        database,
        api_key,
        session,
    ):
        game_id = self.get_game_id(
            game.name,
            api_key,
            session,
        )

        if not game_id:
            return False

        image_data = self.get_image(
            game_id,
            api_key,
            session,
        )

        if not image_data:
            return False

        base_url = image_data["base_url"]["original"]

        images = image_data.get("images", [])

        filename = None

        for image in images:
            if isinstance(image, dict):
                if (
                        image.get("type") == "boxart"
                        and image.get("side") == "front"
                ):
                    filename = image.get("filename")
                    break

            elif isinstance(image, str):
                filename = image
                break

        if not filename:
            return False

        image_url = f"{base_url}{filename}"

        try:
            response = session.get(
                image_url,
                timeout=TIMEOUT,
            )
        except requests.RequestException:
            return False

        if not response.ok:
            return False

        if not response.content:
            return False

        file_name = os.path.basename(filename)

        game.image.save(
            file_name,
            ContentFile(response.content),
            save=True,
        )

        return True

    @staticmethod
    def get_game_id(
        name,
        api_key,
        session,
    ):
        response = session.get(
            "https://api.thegamesdb.net/v1/Games/ByGameName",
            params={
                "apikey": api_key,
                "name": name,
            },
            timeout=TIMEOUT,
        )

        if not response.ok:
            return None

        try:
            data = response.json()
        except ValueError:
            return None

        games = (
            data
            .get("data", {})
            .get("games", [])
        )

        if not games:
            return None

        return games[0].get("id")

    @staticmethod
    def get_image(
        game_id,
        api_key,
        session,
    ):
        response = session.get(
            API_URL,
            params={
                "apikey": api_key,
                "games_id": game_id,
            },
            timeout=TIMEOUT,
        )

        if not response.ok:
            return None

        try:
            data = response.json()
        except ValueError:
            return None

        if data.get("code") != 200:
            return None

        return data.get("data")

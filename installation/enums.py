from django.db import models


class GameRateSource(models.TextChoices):
    METACRITIC = "metacritic", "Metacritic"
    IGN = "ign", "IGN"
    GAMESPOT = "gamespot", "GameSpot"
    IMDB = "imdb", "IMDb"

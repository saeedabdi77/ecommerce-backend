from django.core.management.base import BaseCommand
from django.db import transaction

from provinces_and_cities import Iran

from user.models import City, Province


class Command(BaseCommand):
    help = 'Seed Iranian provinces and cities'

    @transaction.atomic
    def handle(self, *args, **options):
        provinces = {}
        cities = []

        for province in Iran.all:
            province_obj, _ = Province.objects.get_or_create(
                name=province['name'],
            )
            provinces[province['id']] = province_obj

            cities.extend(
                City(
                    province=province_obj,
                    name=city,
                )
                for city in province['cities']
            )

        City.objects.bulk_create(
            cities,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {len(provinces)} provinces '
                f'and {len(cities)} cities.'
            )
        )
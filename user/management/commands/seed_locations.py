from django.core.management.base import BaseCommand
from django.db import transaction

from provinces_and_cities import Iran

from user.models import City, Province


class Command(BaseCommand):
    help = 'Seed Iranian provinces and cities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--database',
            default='default',
        )

    def handle(self, *args, **options):
        database = options['database']
        locations = Iran.all

        with transaction.atomic(using=database):
            provinces = {}

            for province in locations:
                province_obj, _ = Province.objects.using(database).get_or_create(
                    name=province['name'],
                )
                provinces[province['id']] = province_obj.pk

            cities = [
                City(
                    province_id=provinces[province['id']],
                    name=city,
                )
                for province in locations
                for city in province['cities']
            ]

            City.objects.using(database).bulk_create(
                cities,
                ignore_conflicts=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {len(provinces)} provinces '
                f'and {len(cities)} cities into "{database}".'
            )
        )
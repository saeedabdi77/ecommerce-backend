from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = 'Migrate all databases'

    def handle(self, *args, **options):
        for db_name in settings.DATABASES.keys():
            self.stdout.write(f'Migrating database: {db_name}')
            call_command('migrate', database=db_name, interactive=False)

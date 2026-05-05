from django.core.management.base import BaseCommand
from MainApp.seed import run_seed

class Command(BaseCommand):
    help = 'Seeds the database with users, skills, and reviews.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        run_seed()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))

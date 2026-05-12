from django.core.management import BaseCommand, call_command

from projects.models import Project


class Command(BaseCommand):
    help = "Load projects fixture only when the projects table is empty."

    def handle(self, *args, **options):
        count = Project.objects.count()
        if count > 0:
            self.stdout.write(self.style.SUCCESS(f"Projects already exist ({count}); skipping seed."))
            return

        call_command("loaddata", "projects")
        self.stdout.write(self.style.SUCCESS("Loaded projects fixture because table was empty."))

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from MainApp.models import BookingRequest, Skill


class Command(BaseCommand):
    help = (
        "Remove dummy skills/users created for review-testing. "
        "Deletes Skills whose title starts with 'Dummy ' and any BookingRequests pointing to them. "
        "Optionally deletes users whose username starts with 'dummy_peer_'."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirm deletion (required).",
        )
        parser.add_argument(
            "--delete-dummy-users",
            action="store_true",
            help="Also delete users with username starting with 'dummy_peer_'.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["yes"]:
            raise CommandError(
                "Refusing to delete without confirmation. Re-run with --yes"
            )

        dummy_skills = Skill.objects.filter(title__startswith="Dummy ")
        dummy_skill_ids = list(dummy_skills.values_list("id", flat=True))

        deleted_bookingrequests, _ = BookingRequest.objects.filter(
            skill_id__in=dummy_skill_ids
        ).delete()
        deleted_skills, _ = dummy_skills.delete()

        deleted_users = 0
        if options["delete_dummy_users"]:
            from django.contrib.auth import get_user_model

            UserModel = get_user_model()
            deleted_users, _ = UserModel.objects.filter(
                username__startswith="dummy_peer_"
            ).delete()

        self.stdout.write(self.style.SUCCESS("Dummy seed cleanup complete."))
        self.stdout.write(f"Deleted BookingRequest rows: {deleted_bookingrequests}")
        self.stdout.write(f"Deleted Skill rows: {deleted_skills}")
        if options["delete_dummy_users"]:
            self.stdout.write(f"Deleted user-related rows: {deleted_users}")

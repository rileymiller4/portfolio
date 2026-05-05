from __future__ import annotations

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from MainApp.models import BookingRequest, Skill, UserReview


class Command(BaseCommand):
    help = (
        "Create dummy completed bookings (provided + received) that have not yet been "
        "reviewed by the target user. Does NOT delete existing data."
    )

    FIRST_NAMES = [
        "Alex",
        "Taylor",
        "Jordan",
        "Casey",
        "Morgan",
        "Jamie",
        "Avery",
        "Cameron",
        "Quinn",
        "Parker",
        "Reese",
        "Sage",
        "Kendall",
        "Rowan",
        "Logan",
    ]
    LAST_NAMES = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Username to seed data for (defaults to first non-superuser user).",
        )
        parser.add_argument(
            "--provided",
            type=int,
            default=3,
            help="Number of completed bookings where target user is the provider.",
        )
        parser.add_argument(
            "--received",
            type=int,
            default=3,
            help="Number of completed bookings where target user is the requester.",
        )

    def _get_target_user(self, username: str | None):
        UserModel = get_user_model()

        if username:
            try:
                return UserModel.objects.get(username=username)
            except UserModel.DoesNotExist as exc:
                raise CommandError(f"No user found with username={username!r}") from exc

        # Prefer a real user account (non-superuser) if available
        target = UserModel.objects.filter(is_superuser=False).order_by("id").first()
        if target is not None:
            return target

        target = UserModel.objects.order_by("id").first()
        if target is None:
            raise CommandError(
                "No users exist yet. Create an account first (register in the UI or createsuperuser)."
            )
        return target

    def _get_or_create_dummy_peers(self, count: int):
        UserModel = get_user_model()

        peers = list(UserModel.objects.filter(username__startswith="dummy_peer_").order_by("id"))
        if len(peers) >= count:
            return peers

        to_create = count - len(peers)
        for i in range(len(peers) + 1, len(peers) + to_create + 1):
            username = f"dummy_peer_{i}"
            first = random.choice(self.FIRST_NAMES)
            last = random.choice(self.LAST_NAMES)
            peer, created = UserModel.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"{first.lower()}.{last.lower()}{i}@example.com",
                },
            )
            if created:
                peer.set_password("Pass12345!")
                peer.save(update_fields=["password"])
            peers.append(peer)

        return peers

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        provided = max(0, int(options["provided"]))
        received = max(0, int(options["received"]))

        target = self._get_target_user(username)

        created_provided = 0
        created_received = 0

        already_reviewed_ids = set(
            UserReview.objects.filter(reviewer=target).values_list("reviewee_id", flat=True)
        )

        # Seed "provided": target owns an existing skill; a peer is requester.
        target_skills = list(Skill.objects.filter(owner=target).order_by("-created_at"))
        if provided and not target_skills:
            raise CommandError(
                f"User {target.username!r} has no skills yet, so we can't create 'provided' completed sessions. "
                "Create at least one skill first."
            )

        peers = self._get_or_create_dummy_peers(max(2, provided + received))

        attempts = 0
        while created_provided < provided and attempts < (provided + 10) * 5:
            attempts += 1
            peer = random.choice(peers)
            if peer.id == target.id or peer.id in already_reviewed_ids:
                continue

            skill = random.choice(target_skills)
            BookingRequest.objects.create(
                skill=skill,
                requester=peer,
                status="completed",
                slot=None,
            )
            created_provided += 1

        # Seed "received": use an existing skill from someone else; target is requester.
        available_received_skills = Skill.objects.exclude(owner=target).exclude(
            owner__username__startswith="dummy_peer_"
        )
        if received and not available_received_skills.exists():
            raise CommandError(
                "No non-dummy skills exist to create 'received' completed sessions. Seed skills first."
            )

        attempts = 0
        while created_received < received and attempts < (received + 10) * 5:
            attempts += 1

            skill = available_received_skills.order_by("?").first()
            if skill is None:
                break

            provider_id = skill.owner_id
            if provider_id == target.id or provider_id in already_reviewed_ids:
                continue

            BookingRequest.objects.create(
                skill=skill,
                requester=target,
                status="completed",
                slot=None,
            )
            created_received += 1

        if created_provided < provided or created_received < received:
            self.stdout.write(
                self.style.WARNING(
                    "Seeded fewer items than requested (likely due to existing reviews)."
                )
            )

        self.stdout.write(self.style.SUCCESS("Dummy completed, unreviewed sessions created."))
        self.stdout.write(f"Target user: {target.username} (id={target.id})")
        self.stdout.write(f"Completed provided created: {created_provided}")
        self.stdout.write(f"Completed received created: {created_received}")
        self.stdout.write("Tip: open the dashboard and look under Completed History.")

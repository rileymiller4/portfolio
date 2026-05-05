from __future__ import annotations

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Give existing dummy_peer_* users realistic first/last names (no deletions)."

    _FIRST_NAMES = [
        "Alex", "Taylor", "Jordan", "Casey", "Morgan", "Jamie", "Avery", "Cameron",
        "Quinn", "Parker", "Reese", "Sage", "Kendall", "Rowan", "Logan",
    ]
    _LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Optional random seed for repeatable names.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        seed = options.get("seed")
        if seed is not None:
            random.seed(seed)

        UserModel = get_user_model()
        peers = list(UserModel.objects.filter(username__startswith="dummy_peer_").order_by("id"))

        updated = 0
        for peer in peers:
            first = random.choice(self._FIRST_NAMES)
            last = random.choice(self._LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}{peer.id}@example.com"

            changed = False
            if peer.first_name != first:
                peer.first_name = first
                changed = True
            if peer.last_name != last:
                peer.last_name = last
                changed = True
            if peer.email != email:
                peer.email = email
                changed = True

            if changed:
                peer.save(update_fields=["first_name", "last_name", "email"])
                updated += 1

        self.stdout.write(self.style.SUCCESS("Dummy peer normalization complete."))
        self.stdout.write(f"Dummy peer users found: {len(peers)}")
        self.stdout.write(f"Users updated: {updated}")

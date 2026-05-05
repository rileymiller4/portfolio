import os
import sys
from pathlib import Path

import django


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from projects.models import Project  # noqa: PLC0415

    project = Project.objects.get(slug="campus-skillswap-django-project")

    project.tools_used = "\n".join(
        [
            "Python",
            "Django (auth, models, views, templates)",
            "SQLite",
            "Bootstrap 5",
            "Django Forms",
            "Django Messages",
        ]
    )

    project.key_features = "\n".join(
        [
            "Auth (register/login/logout)",
            "Post and manage skills (CRUD + dashboard)",
            "Search by title + category",
            "Booking workflow (request/approve/deny/complete)",
            "Reviews + ratings after completion",
            "Bootstrap UI + Django admin",
        ]
    )

    project.role_contribution = (
        "Built the full-stack Django app end-to-end: models, forms, views, templates, "
        "authentication, and workflow features (search, bookings, reviews)."
    )

    project.demo_url = "/skillswap/"

    project.save(update_fields=["tools_used", "key_features", "role_contribution", "demo_url", "updated_at"])
    print("Updated SkillSwap project portfolio text.")


if __name__ == "__main__":
    main()

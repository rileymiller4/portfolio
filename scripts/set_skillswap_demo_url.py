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
    project.demo_url = "/skillswap/"
    project.save(update_fields=["demo_url", "updated_at"])

    print("Updated demo_url:", project.demo_url)


if __name__ == "__main__":
    main()

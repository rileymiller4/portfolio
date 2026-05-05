import os
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import django

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _safe_name(name: str) -> str:
    name = name.strip().replace(" ", "-")
    name = re.sub(r"[^A-Za-z0-9._-]+", "", name)
    return name or "file"


def extract_docx_text(docx_path: Path) -> str:
    with zipfile.ZipFile(docx_path) as zf:
        xml_bytes = zf.read("word/document.xml")

    root = ET.fromstring(xml_bytes)

    paragraphs: list[str] = []
    for p in root.iter(f"{{{W_NS}}}p"):
        text_parts: list[str] = []
        for t in p.iter(f"{{{W_NS}}}t"):
            if t.text:
                text_parts.append(t.text)
        paragraph = "".join(text_parts).strip()
        if paragraph:
            paragraphs.append(paragraph)

    return "\n".join(paragraphs).strip()


def usage() -> None:
    print(
        "Usage:\n"
        "  python scripts/set_google_ai_studio_assets.py <image_path> [prompt_docx_path]\n\n"
        "Examples:\n"
        "  python scripts/set_google_ai_studio_assets.py C:\\path\\to\\dino.png C:\\path\\to\\dinoprompt.docx\n"
        "  python scripts/set_google_ai_studio_assets.py assets/dino.png assets/dinoprompt.docx\n\n"
        "Notes:\n"
        "- Copies the image into media/projects/ and attaches it to the Google AI Studio project.\n"
        "- If prompt_docx_path is provided, imports its text into prompt_text.\n"
    )


def main() -> None:
    if len(sys.argv) < 2:
        usage()
        raise SystemExit(2)

    project_root = Path(__file__).resolve().parents[1]

    image_path = Path(sys.argv[1]).expanduser()
    if not image_path.is_absolute():
        image_path = project_root / image_path

    prompt_docx_path: Path | None = None
    if len(sys.argv) >= 3:
        prompt_docx_path = Path(sys.argv[2]).expanduser()
        if not prompt_docx_path.is_absolute():
            prompt_docx_path = project_root / prompt_docx_path

    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    if prompt_docx_path is not None and not prompt_docx_path.exists():
        raise SystemExit(f"Docx not found: {prompt_docx_path}")

    media_dir = project_root / "media" / "projects"
    media_dir.mkdir(parents=True, exist_ok=True)

    dest_name = _safe_name(image_path.name)
    dest_path = media_dir / dest_name
    shutil.copy2(image_path, dest_path)

    prompt_text = ""
    if prompt_docx_path is not None:
        prompt_text = extract_docx_text(prompt_docx_path)

    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from projects.models import Project  # noqa: PLC0415

    project = Project.objects.get(slug="google-ai-studio-media-project")
    project.image = f"projects/{dest_name}"

    update_fields = ["image", "updated_at"]
    if prompt_text:
        project.prompt_text = prompt_text
        update_fields.append("prompt_text")

    project.save(update_fields=update_fields)
    print("Attached image to Google AI Studio project:", project.image)
    if prompt_text:
        print("Imported prompt_text (chars):", len(prompt_text))


if __name__ == "__main__":
    main()

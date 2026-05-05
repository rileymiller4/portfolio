import os
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import django


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


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


def main() -> None:
    if len(sys.argv) < 3:
        print(
            "Usage: python scripts/import_prompt_docx_to_project.py <slug> <path-to-docx>\n"
            "Example: python scripts/import_prompt_docx_to_project.py google-ai-studio-media-project assets/dinoprompt.docx"
        )
        raise SystemExit(2)

    slug = sys.argv[1].strip()
    docx_path = Path(sys.argv[2]).expanduser()

    project_root = Path(__file__).resolve().parents[1]
    if not docx_path.is_absolute():
        docx_path = project_root / docx_path

    if not docx_path.exists():
        raise SystemExit(f"Docx not found: {docx_path}")

    prompt_text = extract_docx_text(docx_path)
    if not prompt_text:
        raise SystemExit("No text found in docx.")

    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from projects.models import Project  # noqa: PLC0415

    project = Project.objects.get(slug=slug)
    project.prompt_text = prompt_text
    project.save(update_fields=["prompt_text", "updated_at"])

    print(f"Updated prompt_text for: {project.title} ({project.slug})")


if __name__ == "__main__":
    main()

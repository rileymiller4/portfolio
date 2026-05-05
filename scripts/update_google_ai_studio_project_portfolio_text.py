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

    project = Project.objects.get(slug="google-ai-studio-media-project")

    project.one_sentence_summary = (
        "Recreated a Jurassic Park-style scene with a twist using a multimodal image-to-video workflow."
    )

    project.business_problem = (
        "Video is one of the fastest ways to communicate an idea, but creating a short cinematic scene usually "
        "requires time, equipment, and editing skills. This project explores how multimodal AI tools can speed up "
        "prototyping for storytelling, marketing concepts, and demo content while keeping results coherent."
    )

    project.tools_used = "\n".join(
        [
            "Google AI Studio (video generation tools)",
            "Gemini / LLM prompting (scene + shot descriptions)",
            "Image generator (Nano Banana or equivalent) for ingredients/frames",
            "Prompt iteration + style constraints",
            "Basic video review/editing (optional)",
        ]
    )

    project.key_features = "\n".join(
        [
            "Designed character/location/style 'ingredients' for consistent shots",
            "Recreated a recognizable Jurassic Park-like moment with accurate composition and mood",
            "Used detailed prompts for camera, lighting, and motion to guide animation",
            "Changed the outcome using Extend / Jump-to to create an alternate ending",
            "Documented what prompt details improved coherence and what caused drift",
        ]
    )

    project.role_contribution = (
        "Planned the scene, wrote the prompts, generated the ingredient images/frames, and iterated until the "
        "video matched the intended story beat and visual style."
    )

    project.biggest_challenge = (
        "Maintaining character and environment consistency across frames while still getting believable motion "
        "(AI models tend to drift unless prompts and reference images are very specific)."
    )

    project.what_i_learned = (
        "How to storyboard an AI video, write prompts that specify camera + motion + style, and evaluate outputs "
        "based on consistency and storytelling—not just visual quality."
    )

    project.save(
        update_fields=[
            "one_sentence_summary",
            "business_problem",
            "tools_used",
            "key_features",
            "role_contribution",
            "biggest_challenge",
            "what_i_learned",
            "updated_at",
        ]
    )
    print("Updated Google AI Studio Media Project portfolio text.")


if __name__ == "__main__":
    main()

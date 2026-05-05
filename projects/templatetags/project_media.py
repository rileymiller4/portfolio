from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from django import template

register = template.Library()


@register.filter
def embed_url(url: str | None) -> str:
    """Convert a video share URL into an embeddable URL (YouTube/Vimeo).

    Returns an empty string when the URL isn't recognized.
    """

    if not url:
        return ""

    url = url.strip()
    if not url:
        return ""

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()

    # YouTube
    if "youtube.com" in host:
        qs = parse_qs(parsed.query or "")
        video_id = (qs.get("v") or [""])[0]
        if video_id:
            return f"https://www.youtube-nocookie.com/embed/{video_id}"

    if "youtu.be" in host:
        video_id = (parsed.path or "").lstrip("/").split("/")[0]
        if video_id:
            return f"https://www.youtube-nocookie.com/embed/{video_id}"

    # Vimeo
    if "vimeo.com" in host:
        match = re.search(r"/([0-9]+)", parsed.path or "")
        if match:
            return f"https://player.vimeo.com/video/{match.group(1)}"

    return ""

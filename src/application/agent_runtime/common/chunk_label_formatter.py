from __future__ import annotations

from typing import Any


def chunk_display_title(chunk: dict[str, Any], *, fallback: str = "Chunk") -> str:
    title = chunk.get("section_title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    section_path = chunk.get("section_path")
    if isinstance(section_path, list) and section_path:
        return str(section_path[-1])
    chunk_type = chunk.get("chunk_type")
    return str(chunk_type) if chunk_type else fallback

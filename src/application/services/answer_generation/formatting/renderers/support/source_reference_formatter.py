from __future__ import annotations

from collections.abc import Iterable


def format_page_label(
    page_start: int | None,
    page_end: int | None,
) -> str | None:
    if page_start is None:
        return None
    if page_end is None or page_end == page_start:
        return f"p.{page_start}"
    return f"pp.{page_start}-{page_end}"


def combine_page_labels(labels: Iterable[str | None]) -> str | None:
    unique: list[str] = []
    for label in labels:
        if not label or label in unique:
            continue
        unique.append(label)
    if not unique:
        return None
    return ", ".join(unique)


def simplify_section_path(
    section_path: str | None,
    *,
    max_depth: int = 2,
) -> str | None:
    if not section_path:
        return None
    segments = [segment.strip() for segment in str(section_path).split(">") if segment.strip()]
    if not segments:
        return None
    if len(segments) <= max_depth:
        return " > ".join(segments)
    return " > ".join(segments[-max_depth:])

from src.application.workflows.parsing.builders.chunking.text.section_path_sanitizer import (
    sanitize_section_path,
)
from src.application.workflows.parsing.builders.section_hierarchy.numbering.heading_numbering import (
    strip_heading_number,
)


def normalize_section_path_for_matching(
    section_path: list[str],
    *,
    document_title: str | None = None,
) -> list[str]:
    sanitized_path = sanitize_section_path(
        list(section_path),
        document_title=document_title,
    )
    normalized_parts: list[str] = []

    for part in sanitized_path:
        stripped_part = strip_heading_number(part).strip()
        normalized = " ".join(stripped_part.split())
        if not normalized:
            normalized = " ".join(str(part or "").split())
        if not normalized:
            continue
        if normalized_parts and normalized_parts[-1].casefold() == normalized.casefold():
            continue
        normalized_parts.append(normalized)

    return normalized_parts


def normalized_section_path_text(
    section_path: list[str],
    *,
    document_title: str | None = None,
) -> str:
    return " > ".join(
        normalize_section_path_for_matching(
            section_path,
            document_title=document_title,
        )
    )

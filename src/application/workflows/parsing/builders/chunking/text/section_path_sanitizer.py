import re

_BRANDING_PARTS = {
    "environmentally",
    "responsible solutions",
    "engineered",
    "environmentally responsible solutions engineered",
}
_RESET_MARKERS = {
    "table of contents",
    "contents",
}


def sanitize_section_path(
    section_path: list[str],
    *,
    document_title: str | None = None,
) -> list[str]:
    cleaned_parts: list[str] = []
    document_title_normalized = _normalize(document_title)

    for raw_part in section_path:
        cleaned = str(raw_part or "").strip()
        normalized = _normalize(cleaned)
        if not normalized:
            continue

        if normalized in _RESET_MARKERS:
            cleaned_parts = []
            continue

        if normalized in _BRANDING_PARTS and len(section_path) > 1:
            continue

        if (
            cleaned_parts
            and _normalize(cleaned_parts[-1]) == normalized
        ):
            continue

        cleaned_parts.append(cleaned)

    if (
        len(cleaned_parts) > 1
        and document_title_normalized
        and _normalize(cleaned_parts[0]) == document_title_normalized
    ):
        cleaned_parts = cleaned_parts[1:]

    return cleaned_parts


def _normalize(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())

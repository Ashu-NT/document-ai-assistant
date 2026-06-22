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
_SECTION_NUMBER_PATTERN = re.compile(r"\b(\d+(?:\.\d+)+)\b")


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

        sibling_reset_index = _find_sibling_reset_index(
            cleaned_parts=cleaned_parts,
            current_part=cleaned,
        )
        if sibling_reset_index is not None:
            cleaned_parts = cleaned_parts[:sibling_reset_index]

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


def _find_sibling_reset_index(
    *,
    cleaned_parts: list[str],
    current_part: str,
) -> int | None:
    current_number = _extract_section_number(current_part)
    if current_number is None or len(current_number) < 2:
        return None

    current_parent = current_number[:-1]
    current_depth = len(current_number)
    for index in range(len(cleaned_parts) - 1, -1, -1):
        previous_number = _extract_section_number(cleaned_parts[index])
        if previous_number is None:
            continue
        if previous_number == current_number:
            return None
        if (
            len(previous_number) == current_depth
            and previous_number[:-1] == current_parent
        ):
            return index
    return None


def _extract_section_number(value: str | None) -> tuple[int, ...] | None:
    normalized = _normalize(value)
    match = _SECTION_NUMBER_PATTERN.search(normalized)
    if match is None:
        return None

    try:
        return tuple(int(part) for part in match.group(1).split("."))
    except ValueError:
        return None

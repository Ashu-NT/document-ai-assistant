import re
from functools import lru_cache

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
_LEADING_NUMBER_PATTERN = re.compile(
    r"^\s*(?:chapter|section|part)?\s*(?P<number>\d+(?:\.\d+)*)\b",
    re.IGNORECASE,
)
_TRAILING_NUMBER_PATTERN = re.compile(
    r"(?P<prefix>.*?\S)\s+(?P<number>\d+\.\d+(?:\.\d+)*)\s*$"
)
_WHITESPACE_PATTERN = re.compile(r"\s+")


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

        numbering_reset_index = _find_numbering_conflict_reset_index(
            cleaned_parts=cleaned_parts,
            current_part=cleaned,
        )
        if numbering_reset_index is not None:
            cleaned_parts = cleaned_parts[:numbering_reset_index]

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


@lru_cache(maxsize=8192)
def _normalize(value: str | None) -> str:
    return _WHITESPACE_PATTERN.sub(" ", str(value or "").strip().lower())


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


def _find_numbering_conflict_reset_index(
    *,
    cleaned_parts: list[str],
    current_part: str,
) -> int | None:
    current_number = _extract_section_number(current_part)
    if current_number is None:
        return None

    numbered_indexes = [
        index
        for index, part in enumerate(cleaned_parts)
        if _extract_section_number(part) is not None
    ]
    if not numbered_indexes:
        return None

    best_prefix_index = None
    for index in numbered_indexes:
        previous_number = _extract_section_number(cleaned_parts[index])
        if previous_number is None:
            continue
        if current_number[: len(previous_number)] == previous_number:
            best_prefix_index = index

    if best_prefix_index is not None:
        has_incompatible_descendant = any(
            (
                previous_number := _extract_section_number(cleaned_parts[index])
            ) is not None
            and current_number[: len(previous_number)] != previous_number
            for index in numbered_indexes
            if index > best_prefix_index
        )
        if has_incompatible_descendant:
            return best_prefix_index + 1
        return None

    return numbered_indexes[0]


@lru_cache(maxsize=8192)
def _extract_section_number(value: str | None) -> tuple[int, ...] | None:
    heading_number = _extract_heading_number_text(value)
    if heading_number is None:
        return None

    try:
        return tuple(int(part) for part in heading_number.split("."))
    except ValueError:
        return None


@lru_cache(maxsize=8192)
def _extract_heading_number_text(value: str | None) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None

    leading_match = _LEADING_NUMBER_PATTERN.match(text)
    if leading_match is not None:
        return leading_match.group("number")

    trailing_match = _TRAILING_NUMBER_PATTERN.match(text)
    if trailing_match is None:
        return None

    return trailing_match.group("number")

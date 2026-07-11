from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")
_DIGIT_ONLY_RE = re.compile(r"^\d+$")
_OPTION_SELECTION_RE = re.compile(r"^(?:option|choose|select)\s+(\d+)$")

_QUESTION_CURRENT_REFERENCES = (
    " this document",
    " this manual",
    " this report",
    " this certificate",
    " this drawing",
    " this datasheet",
    " it",
)


def normalize_route_input(value: str) -> str:
    return _WHITESPACE_RE.sub(" ", value.strip().lower())


def strip_prefix(value: str, prefixes: tuple[str, ...]) -> str | None:
    for prefix in prefixes:
        if value.startswith(prefix):
            stripped = value[len(prefix) :].strip()
            return stripped or None
    return None


def extract_candidate_index(value: str) -> int | None:
    if not value:
        return None
    if _DIGIT_ONLY_RE.fullmatch(value):
        return max(int(value) - 1, 0)
    match = _OPTION_SELECTION_RE.fullmatch(value)
    if match is None:
        return None
    return max(int(match.group(1)) - 1, 0)


def references_current_document(value: str) -> bool:
    if value in {"answer this document", "answer from this document"}:
        return True
    return any(reference in f" {value}" for reference in _QUESTION_CURRENT_REFERENCES)

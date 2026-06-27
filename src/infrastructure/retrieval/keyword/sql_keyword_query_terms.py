_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "should",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "with",
}
import re

_NORMALIZED_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def extract_query_terms(query_text: str) -> list[str]:
    return [
        term
        for term in _NORMALIZED_TOKEN_PATTERN.findall((query_text or "").lower())
        if len(term) > 1 and term not in _STOP_WORDS
    ]


def normalize_query_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(_NORMALIZED_TOKEN_PATTERN.findall(value.lower()))

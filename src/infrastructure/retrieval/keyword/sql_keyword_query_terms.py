from src.shared.text import normalize_alnum_text, tokenize_alnum

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


def extract_query_terms(query_text: str) -> list[str]:
    return [
        term
        for term in tokenize_alnum(query_text)
        if len(term) > 1 and term not in _STOP_WORDS
    ]


def normalize_query_text(value: str | None) -> str:
    return normalize_alnum_text(value)

import re

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def normalize_free_text(value: str | None) -> str:
    if not value:
        return ""

    tokens = _TOKEN_PATTERN.findall(value.lower())
    return " ".join(tokens)


def tokenize_text(value: str | None) -> list[str]:
    normalized = normalize_free_text(value)
    if not normalized:
        return []
    return normalized.split()


def normalize_path_segments(path: list[str] | tuple[str, ...] | None) -> list[str]:
    if not path:
        return []

    normalized_segments: list[str] = []
    for segment in path:
        normalized = normalize_free_text(segment)
        if normalized:
            normalized_segments.append(normalized)

    return normalized_segments

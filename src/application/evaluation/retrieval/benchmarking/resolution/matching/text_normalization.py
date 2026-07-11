from src.shared.text.alnum_tokenizer import normalize_alnum_text, tokenize_alnum


def normalize_free_text(value: str | None) -> str:
    return normalize_alnum_text(value)


def tokenize_text(value: str | None) -> list[str]:
    return tokenize_alnum(value)


def normalize_path_segments(path: list[str] | tuple[str, ...] | None) -> list[str]:
    if not path:
        return []

    normalized_segments: list[str] = []
    for segment in path:
        normalized = normalize_free_text(segment)
        if normalized:
            normalized_segments.append(normalized)

    return normalized_segments

import re
from collections.abc import Iterable


def clean_chunk_text(text: str | None) -> str | None:
    if text is None:
        return None

    cleaned = re.sub(r"\n{3,}", "\n\n", str(text)).strip()
    return cleaned or None


def count_tokens(text: str | None) -> int:
    if not text:
        return 0

    return len(text.split())


def tail_words(text: str, count: int) -> str:
    if count <= 0:
        return ""

    tokens = text.split()
    if not tokens:
        return ""

    return " ".join(tokens[-count:])


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    for value in values:
        if value in seen:
            continue

        seen.add(value)
        ordered.append(value)

    return ordered


def is_contents_title(value: str | None) -> bool:
    if not value:
        return False

    normalized = re.sub(r"\s+", " ", value).strip().lower()
    return normalized in {"contents", "table of contents", "toc"}


def is_reference_title(value: str | None) -> bool:
    if not value:
        return False

    normalized = re.sub(r"\s+", " ", value).strip().lower()
    return normalized in {
        "bibliography",
        "references",
        "reference",
        "works cited",
    }


def looks_like_boilerplate(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return any(
        marker in normalized
        for marker in (
            "copyright",
            "all rights reserved",
            "alle rechte",
            "isbn",
            "issn",
            "published by",
        )
    )


def is_low_value_fragment(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return True

    if re.fullmatch(r"\d+", normalized):
        return True

    if re.fullmatch(r"[-_./\\]+", normalized):
        return True

    return False

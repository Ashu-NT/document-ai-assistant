import re
from collections.abc import Iterable
from typing import Any


def resolve_parser_extra(element: Any) -> dict:
    if element.parser_metadata is None or element.parser_metadata.extra is None:
        return {}

    return element.parser_metadata.extra


def is_furniture_or_embedded_picture(element: Any) -> bool:
    extra = resolve_parser_extra(element)
    parent_ref = extra.get("parent_ref")
    if isinstance(parent_ref, str) and parent_ref.startswith("#/pictures/"):
        return True

    return extra.get("content_layer") == "furniture"


def clean_chunk_text(text: str | None) -> str | None:
    if text is None:
        return None

    cleaned = re.sub(r"\n{3,}", "\n\n", str(text)).strip()
    return cleaned or None


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    for value in values:
        if value in seen:
            continue

        seen.add(value)
        ordered.append(value)

    return ordered


def common_path_prefix(paths: list[list[str]]) -> list[str]:
    if not paths:
        return []

    prefix = list(paths[0])
    for path in paths[1:]:
        prefix = [
            left
            for left, right in zip(prefix, path)
            if left == right
        ]
        if not prefix:
            return []

    return prefix


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

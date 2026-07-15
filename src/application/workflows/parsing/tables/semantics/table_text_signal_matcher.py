from __future__ import annotations

import re
from collections.abc import Iterable

from src.domain.assets.table_rows.table_row_patterns import looks_interval_header

_NORMALIZE_PATTERN = re.compile(r"[^\w]+")


class TableTextSignalMatcher:
    def normalized_text(self, *parts: object) -> str:
        normalized_parts = [
            _normalize_text(part)
            for part in parts
            if _normalize_text(part)
        ]
        return " ".join(normalized_parts)

    def contains(self, text: str, phrase: str) -> bool:
        normalized_text = _pad_text(_normalize_text(text))
        normalized_phrase = _normalize_text(phrase)
        if not normalized_text or not normalized_phrase:
            return False
        return _pad_text(normalized_phrase) in normalized_text

    def count_unique(self, text: str, markers: Iterable[str]) -> int:
        return sum(1 for marker in markers if self.contains(text, marker))

    def count_interval_header_tokens(self, headers: list[str]) -> int:
        count = 0
        for header in headers:
            normalized_header = _normalize_text(header)
            if not normalized_header:
                continue
            if looks_interval_header(normalized_header):
                count += 1
                continue
            tokens = [token for token in normalized_header.split() if token]
            if tokens and all(looks_interval_header(token) for token in tokens):
                count += len(tokens)
        return count


def _normalize_text(value: object) -> str:
    text = _NORMALIZE_PATTERN.sub(" ", str(value or "").casefold()).strip()
    return " ".join(text.split())


def _pad_text(value: str) -> str:
    return f" {value.strip()} " if value.strip() else ""

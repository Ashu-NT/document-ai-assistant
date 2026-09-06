from __future__ import annotations

import re
from collections.abc import Iterator
from functools import lru_cache

from .models import (
    EvidenceMarker,
    MarkerMatch,
)


class StructuredMarkerMatcher:
    """Matches structured evidence markers against document text.

    This class performs lexical matching only.

    It does NOT decide:
    - whether a match is strong enough;
    - which evidence family wins;
    - which ChunkType should be assigned.

    Those decisions belong to higher-level policies.
    """

    def normalize(
        self,
        value: str | None,
    ) -> str:
        normalized = re.sub(
            r"[\W_]+",
            " ",
            str(value or ""),
            flags=re.UNICODE,
        )

        return " ".join(
            normalized.strip().lower().split()
        )

    def iter_matches(
        self,
        text: str | None,
        marker: EvidenceMarker,
    ) -> Iterator[MarkerMatch]:
        yield from self.iter_normalized_matches(self.normalize(text), marker)

    def iter_normalized_matches(
        self,
        normalized_text: str,
        marker: EvidenceMarker,
    ) -> Iterator[MarkerMatch]:
        normalized_marker = _normalize_marker(marker.text)

        if not normalized_text or not normalized_marker:
            return

        start = normalized_text.find(normalized_marker)
        while start >= 0:
            end = start + len(normalized_marker)
            has_left_boundary = start == 0 or normalized_text[start - 1] == " "
            has_right_boundary = end == len(normalized_text) or normalized_text[end] == " "
            if has_left_boundary and has_right_boundary:
                yield MarkerMatch(
                    marker=marker,
                    start=start,
                    end=end,
                )
            start = normalized_text.find(normalized_marker, start + 1)

    def find_matches(
        self,
        text: str | None,
        markers: tuple[EvidenceMarker, ...],
    ) -> tuple[MarkerMatch, ...]:
        return self.find_normalized_matches(self.normalize(text), markers)

    def find_normalized_matches(
        self,
        normalized_text: str,
        markers: tuple[EvidenceMarker, ...],
    ) -> tuple[MarkerMatch, ...]:
        matches: list[MarkerMatch] = []
        for marker in markers:
            matches.extend(self.iter_normalized_matches(normalized_text, marker))
        return tuple(matches)

    def contains(
        self,
        text: str | None,
        marker: EvidenceMarker,
    ) -> bool:
        return self.contains_normalized(self.normalize(text), marker)

    def contains_normalized(
        self,
        normalized_text: str,
        marker: EvidenceMarker,
    ) -> bool:
        return self._contains_normalized_phrase(
            normalized_text,
            _normalize_marker(marker.text),
        )

    def contains_any(
        self,
        text: str | None,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return self.contains_any_normalized(self.normalize(text), markers)

    def contains_any_normalized(
        self,
        normalized_text: str,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return any(
            self.contains_normalized(normalized_text, marker)
            for marker in markers
        )

    def contains_term(
        self,
        text: str | None,
        term: str,
    ) -> bool:
        return self._contains_normalized_term(self.normalize(text), term)

    def contains_any_term(
        self,
        text: str | None,
        terms: tuple[str, ...],
    ) -> bool:
        normalized_text = self.normalize(text)
        return any(
            self._contains_normalized_term(normalized_text, term)
            for term in terms
        )

    def contains_any_term_normalized(
        self,
        normalized_text: str,
        terms: tuple[str, ...],
    ) -> bool:
        return any(
            self._contains_normalized_term(normalized_text, term)
            for term in terms
        )

    def _contains_normalized_term(self, normalized_text: str, term: str) -> bool:
        normalized_term = _normalize_marker(term)
        return self._contains_normalized_phrase(normalized_text, normalized_term)

    @staticmethod
    def _contains_normalized_phrase(
        normalized_text: str,
        normalized_phrase: str,
    ) -> bool:
        if not normalized_text or not normalized_phrase:
            return False
        start = normalized_text.find(normalized_phrase)
        while start >= 0:
            end = start + len(normalized_phrase)
            if (start == 0 or normalized_text[start - 1] == " ") and (
                end == len(normalized_text) or normalized_text[end] == " "
            ):
                return True
            start = normalized_text.find(normalized_phrase, start + 1)
        return False


@lru_cache(maxsize=2048)
def _normalize_marker(value: str) -> str:
    normalized = re.sub(r"[\W_]+", " ", value, flags=re.UNICODE)
    return " ".join(normalized.strip().lower().split())

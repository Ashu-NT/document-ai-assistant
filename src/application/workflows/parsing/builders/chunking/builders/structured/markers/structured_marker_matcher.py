from __future__ import annotations

import re
from collections.abc import Iterator

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
        normalized_text = self.normalize(text)
        normalized_marker = self.normalize(marker.text)

        if not normalized_text or not normalized_marker:
            return

        pattern = re.compile(
            rf"(?<!\w){re.escape(normalized_marker)}(?!\w)"
        )

        for match in pattern.finditer(normalized_text):
            yield MarkerMatch(
                marker=marker,
                start=match.start(),
                end=match.end(),
            )

    def find_matches(
        self,
        text: str | None,
        markers: tuple[EvidenceMarker, ...],
    ) -> tuple[MarkerMatch, ...]:
        matches: list[MarkerMatch] = []

        for marker in markers:
            matches.extend(
                self.iter_matches(
                    text,
                    marker,
                )
            )

        return tuple(matches)

    def contains(
        self,
        text: str | None,
        marker: EvidenceMarker,
    ) -> bool:
        return next(
            self.iter_matches(text, marker),
            None,
        ) is not None

    def contains_any(
        self,
        text: str | None,
        markers: tuple[EvidenceMarker, ...],
    ) -> bool:
        return any(
            self.contains(text, marker)
            for marker in markers
        )
        
    def contains_term(
        self,
        text: str | None,
        term: str,
    ) -> bool:
        normalized_text = self.normalize(text)
        normalized_term = self.normalize(term)

        if not normalized_text or not normalized_term:
            return False

        pattern = re.compile(
            rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
        )

        return pattern.search(normalized_text) is not None


    def contains_any_term(
        self,
        text: str | None,
        terms: tuple[str, ...],
    ) -> bool:
        return any(
            self.contains_term(text, term)
            for term in terms
        )
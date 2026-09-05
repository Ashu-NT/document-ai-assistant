from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarkerStrength(StrEnum):
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"


@dataclass(frozen=True, slots=True)
class EvidenceMarker:
    text: str
    strength: MarkerStrength

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError(
                "EvidenceMarker.text must not be empty."
            )


@dataclass(frozen=True, slots=True)
class MarkerMatch:
    marker: EvidenceMarker
    start: int
    end: int


class MarkerQualificationReason(StrEnum):
    NO_EVIDENCE = "no_evidence"
    STRONG_MARKER = "strong_marker"
    SCORE_THRESHOLD = "score_threshold"
    WEAK_ONLY_WITHOUT_CONTEXT = "weak_only_without_context"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True, slots=True)
class MarkerEvidence:
    """Distinct semantic marker evidence found in a candidate text."""

    matches: tuple[MarkerMatch, ...]

    @property
    def markers(self) -> tuple[EvidenceMarker, ...]:
        """Return distinct matched markers.

        Repeating the same marker several times must not artificially
        increase semantic confidence.
        """
        seen: set[EvidenceMarker] = set()
        markers: list[EvidenceMarker] = []

        for match in self.matches:
            if match.marker in seen:
                continue

            seen.add(match.marker)
            markers.append(match.marker)

        return tuple(markers)

    @property
    def strong_count(self) -> int:
        return sum(
            marker.strength == MarkerStrength.STRONG
            for marker in self.markers
        )

    @property
    def medium_count(self) -> int:
        return sum(
            marker.strength == MarkerStrength.MEDIUM
            for marker in self.markers
        )

    @property
    def weak_count(self) -> int:
        return sum(
            marker.strength == MarkerStrength.WEAK
            for marker in self.markers
        )

    @property
    def is_empty(self) -> bool:
        return not self.markers


@dataclass(frozen=True, slots=True)
class MarkerQualificationResult:
    qualified: bool
    score: int
    threshold: int
    evidence: MarkerEvidence
    reason: MarkerQualificationReason
    section_context_matches: bool
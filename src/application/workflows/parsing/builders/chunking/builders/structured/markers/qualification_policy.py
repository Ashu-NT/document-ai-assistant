from __future__ import annotations

from dataclasses import dataclass

from .models import (
    MarkerEvidence,
    MarkerMatch,
    MarkerQualificationReason,
    MarkerQualificationResult,
    MarkerStrength,
)


@dataclass(frozen=True, slots=True)
class MarkerQualificationPolicyConfig:
    strong_weight: int = 4
    medium_weight: int = 2
    weak_weight: int = 1

    qualification_threshold: int = 4
    section_context_bonus: int = 2

    allow_weak_only_without_context: bool = False


class StructuredMarkerQualificationPolicy:
    """Determines whether lexical marker matches constitute sufficient evidence.

    This class owns semantic qualification rules.

    It does not:
    - search text;
    - define marker vocabularies;
    - choose ChunkType;
    - build chunk windows.
    """

    def __init__(
        self,
        config: MarkerQualificationPolicyConfig | None = None,
    ) -> None:
        self.config = (
            config
            or MarkerQualificationPolicyConfig()
        )

    def qualify(
        self,
        *,
        matches: tuple[MarkerMatch, ...],
        section_context_matches: bool = False,
    ) -> MarkerQualificationResult:
        evidence = MarkerEvidence(matches=matches)

        if evidence.is_empty:
            return MarkerQualificationResult(
                qualified=False,
                score=0,
                threshold=self.config.qualification_threshold,
                evidence=evidence,
                reason=MarkerQualificationReason.NO_EVIDENCE,
                section_context_matches=section_context_matches,
            )

        base_score = self._calculate_score(evidence)

        context_bonus = (
            self.config.section_context_bonus
            if section_context_matches
            else 0
        )

        total_score = base_score + context_bonus

        # A highly discriminative marker can independently qualify.
        if evidence.strong_count > 0:
            return MarkerQualificationResult(
                qualified=True,
                score=total_score,
                threshold=self.config.qualification_threshold,
                evidence=evidence,
                reason=MarkerQualificationReason.STRONG_MARKER,
                section_context_matches=section_context_matches,
            )

        # Generic weak terminology must not independently create a
        # semantic family merely because several common words occur.
        if (
            evidence.medium_count == 0
            and evidence.weak_count > 0
            and not section_context_matches
            and not self.config.allow_weak_only_without_context
        ):
            return MarkerQualificationResult(
                qualified=False,
                score=total_score,
                threshold=self.config.qualification_threshold,
                evidence=evidence,
                reason=MarkerQualificationReason.WEAK_ONLY_WITHOUT_CONTEXT,
                section_context_matches=section_context_matches,
            )

        if total_score >= self.config.qualification_threshold:
            return MarkerQualificationResult(
                qualified=True,
                score=total_score,
                threshold=self.config.qualification_threshold,
                evidence=evidence,
                reason=MarkerQualificationReason.SCORE_THRESHOLD,
                section_context_matches=section_context_matches,
            )

        return MarkerQualificationResult(
            qualified=False,
            score=total_score,
            threshold=self.config.qualification_threshold,
            evidence=evidence,
            reason=MarkerQualificationReason.INSUFFICIENT_EVIDENCE,
            section_context_matches=section_context_matches,
        )

    def _calculate_score(
        self,
        evidence: MarkerEvidence,
    ) -> int:
        weights = {
            MarkerStrength.STRONG: self.config.strong_weight,
            MarkerStrength.MEDIUM: self.config.medium_weight,
            MarkerStrength.WEAK: self.config.weak_weight,
        }

        return sum(
            weights[marker.strength]
            for marker in evidence.markers
        )
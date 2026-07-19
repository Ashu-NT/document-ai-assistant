from __future__ import annotations

from src.application.langgraph.reflection.models import (
    SufficiencyVerdict,
    SufficiencyVerdictType,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.evidence_sufficiency_context import (
    EvidenceSufficiencyContext,
)


class GenericEvidenceSufficiencyStrategy:
    """The mandatory default -- built entirely from signals
    `AnswerQualityScorer`/`EvidenceQualityScorer` already compute for every
    question, with no keyword/domain markers. Every `RetrievalQueryIntent`
    without a registered specialization (the overwhelming majority of real
    questions in a general document set) gets a real evaluation from this,
    instead of silently falling through to nothing."""

    def is_answer_sufficient(
        self, context: EvidenceSufficiencyContext
    ) -> SufficiencyVerdict:
        answer_quality = context.answer_quality
        evidence_quality = context.evidence_quality

        if (
            evidence_quality.has_sufficient_evidence
            and answer_quality.contains_requested_information
            and not answer_quality.has_duplicate_content
            and not answer_quality.unexpected_pages
        ):
            return SufficiencyVerdict(
                verdict=SufficiencyVerdictType.SUFFICIENT,
                reason=(
                    "The answer is grounded in sufficient approved evidence "
                    "and addresses the question."
                ),
            )

        missing_information: list[str] = []
        if not evidence_quality.has_sufficient_evidence:
            missing_information.append("supporting evidence for the question")
        if not answer_quality.contains_requested_information:
            missing_information.append("information that directly answers the question")

        return SufficiencyVerdict(
            verdict=SufficiencyVerdictType.INSUFFICIENT_RETRY,
            reason=(
                "The answer does not yet contain enough grounded, "
                "non-duplicated, correctly-referenced information to accept."
            ),
            missing_information=missing_information,
        )

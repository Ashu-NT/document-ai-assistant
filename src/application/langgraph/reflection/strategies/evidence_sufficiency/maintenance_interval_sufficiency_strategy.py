from __future__ import annotations

from src.application.langgraph.reflection.detectors.maintenance_interval_context_detector import (
    is_selected_document_maintenance_interval_context,
)
from src.application.langgraph.reflection.evaluators.maintenance_evidence_relevance_detector import (
    MaintenanceEvidenceRelevanceDetector,
)
from src.application.langgraph.reflection.models import (
    SufficiencyVerdict,
    SufficiencyVerdictType,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.evidence_sufficiency_context import (
    EvidenceSufficiencyContext,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.generic_evidence_sufficiency_strategy import (
    GenericEvidenceSufficiencyStrategy,
)


class MaintenanceIntervalEvidenceSufficiencyStrategy:
    """Registered against `RetrievalQueryIntent.MAINTENANCE`. Wraps the
    existing maintenance-interval context/relevance detection unchanged --
    when the question isn't actually a maintenance-interval question (or no
    interval-shaped evidence exists), falls back to the generic strategy
    rather than returning a domain-specific negative verdict."""

    def __init__(
        self,
        *,
        generic_strategy: GenericEvidenceSufficiencyStrategy | None = None,
    ) -> None:
        self._generic_strategy = generic_strategy or GenericEvidenceSufficiencyStrategy()

    def is_answer_sufficient(
        self, context: EvidenceSufficiencyContext
    ) -> SufficiencyVerdict:
        has_relevant_evidence = MaintenanceEvidenceRelevanceDetector.has_relevant_evidence(
            question=context.question,
            answer_intent=context.answer_intent,
            approved_chunks=context.approved_chunks,
            selected_document_id=context.selected_document_id,
        )
        context_matches = is_selected_document_maintenance_interval_context(
            question=context.question,
            answer_intent=context.answer_intent,
            selected_document_id=context.selected_document_id,
            has_relevant_maintenance_evidence=has_relevant_evidence,
        )
        if context_matches:
            return SufficiencyVerdict(
                verdict=SufficiencyVerdictType.SUFFICIENT,
                reason=(
                    "Grounded maintenance interval evidence exists in the "
                    "selected document."
                ),
            )
        if self._answer_has_interval_structure_the_generic_scorer_missed(context):
            return SufficiencyVerdict(
                verdict=SufficiencyVerdictType.SUFFICIENT,
                reason=(
                    "The answer has clear maintenance interval structure "
                    "even though it shares no question words verbatim."
                ),
            )
        return self._generic_strategy.is_answer_sufficient(context)

    @staticmethod
    def _answer_has_interval_structure_the_generic_scorer_missed(
        context: EvidenceSufficiencyContext,
    ) -> bool:
        """A domain-aware rescue for the exact case the generic term-overlap
        check can't see: an answer that describes maintenance intervals in
        different words than the question (§3.5 -- this used to live as a
        maintenance-specific fallback inside the supposedly-generic
        `AnswerQualityScorer`; it belongs here instead, gated on exactly the
        same other conditions the generic strategy itself requires)."""
        answer_quality = context.answer_quality
        evidence_quality = context.evidence_quality
        return (
            evidence_quality.has_sufficient_evidence
            and not answer_quality.contains_requested_information
            and not answer_quality.has_duplicate_content
            and not answer_quality.unexpected_pages
            and MaintenanceEvidenceRelevanceDetector.question_requests_maintenance_intervals(
                context.question.lower()
            )
            and MaintenanceEvidenceRelevanceDetector.has_interval_structure(
                context.answer_text.lower()
            )
        )

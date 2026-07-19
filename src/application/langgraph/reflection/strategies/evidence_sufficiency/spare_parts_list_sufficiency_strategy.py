from __future__ import annotations

from src.application.langgraph.reflection.detectors.spare_parts_list_context_detector import (
    answer_denies_spare_parts_list,
    answer_only_has_unit_artifact_rows,
    is_legitimate_partial_spare_parts_answer,
    is_selected_document_spare_parts_list_context,
)
from src.application.langgraph.reflection.evaluators.spare_parts_evidence_relevance_detector import (
    SparePartsEvidenceRelevanceDetector,
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


class SparePartsListEvidenceSufficiencyStrategy:
    """Registered against the coarse `RetrievalQueryIntent.TABLE` intent, per
    the explicit design decision that TABLE describes the requested
    operation while "spare parts" describes a property of the retrieved
    content -- this strategy performs its own internal content sniff
    (unchanged from the existing detector) rather than requiring a separate
    intent value, so it correctly no-ops for non-spare-parts table
    questions."""

    def __init__(
        self,
        *,
        generic_strategy: GenericEvidenceSufficiencyStrategy | None = None,
    ) -> None:
        self._generic_strategy = generic_strategy or GenericEvidenceSufficiencyStrategy()

    def is_answer_sufficient(
        self, context: EvidenceSufficiencyContext
    ) -> SufficiencyVerdict:
        has_relevant_evidence = SparePartsEvidenceRelevanceDetector.has_relevant_evidence(
            approved_chunks=context.approved_chunks,
            selected_document_id=context.selected_document_id,
        )
        context_matches = is_selected_document_spare_parts_list_context(
            question=context.question,
            has_relevant_spare_parts_evidence=has_relevant_evidence,
        )
        if not context_matches:
            return self._generic_strategy.is_answer_sufficient(context)

        if is_legitimate_partial_spare_parts_answer(context.answer_text):
            return SufficiencyVerdict(
                verdict=SufficiencyVerdictType.SUFFICIENT,
                reason=(
                    "The answer is grounded in the retrieved spare parts "
                    "table evidence and already lists real sections, pages, "
                    "or parsed rows."
                ),
            )
        if answer_denies_spare_parts_list(
            context.answer_text
        ) or answer_only_has_unit_artifact_rows(context.answer_text):
            return SufficiencyVerdict(
                verdict=SufficiencyVerdictType.INSUFFICIENT_RETRY,
                reason=(
                    "Grounded spare parts table evidence was retrieved, but "
                    "the answer denied a spare parts list exists or only "
                    "contained header/unit artifacts instead of real rows."
                ),
                missing_information=["spare parts table rows"],
            )
        return self._generic_strategy.is_answer_sufficient(context)

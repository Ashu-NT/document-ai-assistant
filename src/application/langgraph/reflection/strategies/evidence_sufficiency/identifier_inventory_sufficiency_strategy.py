from __future__ import annotations

from src.application.langgraph.reflection.detectors.identifier_inventory_context_detector import (
    answer_contains_identifier_inventory,
    is_selected_document_identifier_inventory_context,
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


class IdentifierInventoryEvidenceSufficiencyStrategy:
    """Registered against `RetrievalQueryIntent.IDENTIFIER`. Wraps the
    existing identifier-inventory context/content detection unchanged."""

    def __init__(
        self,
        *,
        generic_strategy: GenericEvidenceSufficiencyStrategy | None = None,
    ) -> None:
        self._generic_strategy = generic_strategy or GenericEvidenceSufficiencyStrategy()

    def is_answer_sufficient(
        self, context: EvidenceSufficiencyContext
    ) -> SufficiencyVerdict:
        context_matches = is_selected_document_identifier_inventory_context(
            question=context.question,
            answer_intent=context.answer_intent,
            selected_document_id=context.selected_document_id,
            has_useful_evidence=context.evidence_quality.has_sufficient_evidence,
        )
        if not context_matches:
            return self._generic_strategy.is_answer_sufficient(context)

        if answer_contains_identifier_inventory(context.answer_text):
            return SufficiencyVerdict(
                verdict=SufficiencyVerdictType.SUFFICIENT,
                reason=(
                    "The answer lists explicit identifier values from the "
                    "grounded document evidence."
                ),
            )
        return SufficiencyVerdict(
            verdict=SufficiencyVerdictType.INSUFFICIENT_RETRY,
            reason=(
                "The answer did not actually list the requested identifiers "
                "even though grounded evidence exists in the selected document."
            ),
            missing_information=["explicit identifier values"],
        )

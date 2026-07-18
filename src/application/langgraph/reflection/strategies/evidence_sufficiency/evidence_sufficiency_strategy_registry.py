from __future__ import annotations

from src.application.langgraph.reflection.models import SufficiencyVerdict
from src.application.langgraph.reflection.strategies.evidence_sufficiency.evidence_sufficiency_context import (
    EvidenceSufficiencyContext,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.evidence_sufficiency_strategy import (
    EvidenceSufficiencyStrategy,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.generic_evidence_sufficiency_strategy import (
    GenericEvidenceSufficiencyStrategy,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.identifier_inventory_sufficiency_strategy import (
    IdentifierInventoryEvidenceSufficiencyStrategy,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.maintenance_interval_sufficiency_strategy import (
    MaintenanceIntervalEvidenceSufficiencyStrategy,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency.spare_parts_list_sufficiency_strategy import (
    SparePartsListEvidenceSufficiencyStrategy,
)

# Keyed on RetrievalQueryIntent.value (lowercase, e.g. "maintenance", "table",
# "identifier") -- see src/application/workflows/retrieval/retrieval_query_intent.py.
# Any intent not present here (the overwhelming majority: TROUBLESHOOTING,
# SAFETY, PROCEDURE, SPECIFICATION, OVERVIEW, FIGURE, GENERAL,
# DOCUMENT_EXPLORATION, and any intent added in the future) uses the generic
# default -- registering a specialization here is opt-in, never required.
_DEFAULT_STRATEGIES_BY_INTENT: dict[str, EvidenceSufficiencyStrategy] = {
    "maintenance": MaintenanceIntervalEvidenceSufficiencyStrategy(),
    "table": SparePartsListEvidenceSufficiencyStrategy(),
    "identifier": IdentifierInventoryEvidenceSufficiencyStrategy(),
}


class EvidenceSufficiencyStrategyRegistry:
    def __init__(
        self,
        *,
        strategies_by_intent: dict[str, EvidenceSufficiencyStrategy] | None = None,
        default_strategy: EvidenceSufficiencyStrategy | None = None,
    ) -> None:
        self._strategies_by_intent = (
            strategies_by_intent
            if strategies_by_intent is not None
            else dict(_DEFAULT_STRATEGIES_BY_INTENT)
        )
        self._default_strategy = default_strategy or GenericEvidenceSufficiencyStrategy()

    def for_intent(self, retrieval_query_intent: str | None) -> EvidenceSufficiencyStrategy:
        key = (retrieval_query_intent or "").strip().lower()
        return self._strategies_by_intent.get(key, self._default_strategy)

    def evaluate(
        self,
        *,
        retrieval_query_intent: str | None,
        context: EvidenceSufficiencyContext,
    ) -> SufficiencyVerdict:
        return self.for_intent(retrieval_query_intent).is_answer_sufficient(context)

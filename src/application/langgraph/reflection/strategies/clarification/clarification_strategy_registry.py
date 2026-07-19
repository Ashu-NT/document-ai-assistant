from __future__ import annotations

from src.application.langgraph.reflection.strategies.clarification.clarification_context import (
    ClarificationContext,
)
from src.application.langgraph.reflection.strategies.clarification.clarification_strategy import (
    ClarificationStrategy,
)
from src.application.langgraph.reflection.strategies.clarification.fixed_options_clarification_strategy import (
    FixedOptionsClarificationStrategy,
)

# Migrated 1:1 from the retired ClarificationBuilder._resolve_options()'s two
# fixed-option branches -- keyed on RetrievalQueryIntent.value now instead of
# a substring match against question text OR answer_intent, so exactly one
# registration applies per query, matching the dispatch pattern already used
# by EvidenceSufficiencyStrategyRegistry/RetryReformulationStrategyRegistry.
_FIXED_OPTIONS_BY_INTENT: dict[str, tuple[str, ...]] = {
    "maintenance": (
        "maintenance tasks",
        "maintenance intervals",
        "maintenance procedures",
    ),
    "specification": (
        "technical specifications",
        "operating limits",
        "dimensions or ratings",
    ),
}


def _default_strategies_by_intent() -> dict[str, ClarificationStrategy]:
    return {
        intent: FixedOptionsClarificationStrategy(fixed_options=options)
        for intent, options in _FIXED_OPTIONS_BY_INTENT.items()
    }


class ClarificationStrategyRegistry:
    def __init__(
        self,
        *,
        strategies_by_intent: dict[str, ClarificationStrategy] | None = None,
        default_strategy: ClarificationStrategy | None = None,
    ) -> None:
        self._strategies_by_intent = (
            strategies_by_intent
            if strategies_by_intent is not None
            else _default_strategies_by_intent()
        )
        self._default_strategy = default_strategy or FixedOptionsClarificationStrategy()

    def for_intent(self, retrieval_query_intent: str | None) -> ClarificationStrategy:
        key = (retrieval_query_intent or "").strip().lower()
        return self._strategies_by_intent.get(key, self._default_strategy)

    def build_options(
        self,
        *,
        retrieval_query_intent: str | None,
        context: ClarificationContext,
    ) -> list[str]:
        return self.for_intent(retrieval_query_intent).build_options(context)

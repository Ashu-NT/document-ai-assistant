from __future__ import annotations

from src.application.langgraph.reflection.models import RetryPlan
from src.application.langgraph.reflection.strategies.retry_reformulation.keyword_expansion_retry_reformulation_strategy import (
    KeywordExpansionRetryReformulationStrategy,
)
from src.application.langgraph.reflection.strategies.retry_reformulation.retry_reformulation_context import (
    RetryReformulationContext,
)
from src.application.langgraph.reflection.strategies.retry_reformulation.retry_reformulation_strategy import (
    RetryReformulationStrategy,
)

# Migrated 1:1 from the retired RetryQueryBuilder._INTENT_EXPANSIONS -- keyed
# on RetrievalQueryIntent.value now instead of a raw substring match against
# answer_intent/question text, so exactly one bucket applies per query
# instead of the old code's "every marker that happens to appear" stacking.
_EXPANSION_TERMS_BY_INTENT: dict[str, tuple[str, ...]] = {
    "maintenance": (
        "maintenance schedule",
        "preventive maintenance",
        "service interval",
        "inspection",
        "lubrication",
    ),
    "specification": (
        "technical data",
        "design pressure",
        "test pressure",
        "dimensions",
        "rating",
    ),
    "procedure": ("procedure", "steps", "remove", "install", "operate"),
    "safety": ("warning", "caution", "danger", "hazard"),
    "troubleshooting": ("fault", "troubleshooting", "problem", "cause", "remedy"),
}


def _default_strategies_by_intent() -> dict[str, RetryReformulationStrategy]:
    return {
        intent: KeywordExpansionRetryReformulationStrategy(expansion_terms=terms)
        for intent, terms in _EXPANSION_TERMS_BY_INTENT.items()
    }


class RetryReformulationStrategyRegistry:
    def __init__(
        self,
        *,
        strategies_by_intent: dict[str, RetryReformulationStrategy] | None = None,
        default_strategy: RetryReformulationStrategy | None = None,
    ) -> None:
        self._strategies_by_intent = (
            strategies_by_intent
            if strategies_by_intent is not None
            else _default_strategies_by_intent()
        )
        self._default_strategy = (
            default_strategy or KeywordExpansionRetryReformulationStrategy()
        )

    def for_intent(self, retrieval_query_intent: str | None) -> RetryReformulationStrategy:
        key = (retrieval_query_intent or "").strip().lower()
        return self._strategies_by_intent.get(key, self._default_strategy)

    def build_retry_plan(
        self,
        *,
        retrieval_query_intent: str | None,
        context: RetryReformulationContext,
    ) -> RetryPlan:
        return self.for_intent(retrieval_query_intent).build_retry_plan(context)

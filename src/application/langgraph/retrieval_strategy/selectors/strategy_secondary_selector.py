from __future__ import annotations

from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
)
from src.application.langgraph.retrieval_strategy.policies import RetrievalStrategyPolicy
from src.application.workflows.shared.maintenance_signal_detection import (
    mentions_maintenance_interval,
)


def select_secondary_strategies(
    *,
    context: RetrievalContext,
    ranked: list[RetrievalStrategy],
    scores: dict[RetrievalStrategy, float],
    primary: RetrievalStrategy,
    policy: RetrievalStrategyPolicy,
) -> list[RetrievalStrategy]:
    if not policy.allow_multi_strategy:
        return []

    allowed = [
        strategy
        for strategy in ranked[1:]
        if scores.get(strategy, 0.0) >= 4.0
    ]
    if (
        primary == RetrievalStrategy.MAINTENANCE_LOOKUP
        and _looks_like_maintenance_interval_query(context)
        and RetrievalStrategy.TABLE_LOOKUP in ranked
        and RetrievalStrategy.TABLE_LOOKUP not in allowed
    ):
        allowed = [RetrievalStrategy.TABLE_LOOKUP, *allowed]
    if primary in {
        RetrievalStrategy.MAINTENANCE_LOOKUP,
        RetrievalStrategy.PROCEDURE_LOOKUP,
        RetrievalStrategy.TECHNICAL_SPECIFICATION,
        RetrievalStrategy.CERTIFICATION_LOOKUP,
    } and RetrievalStrategy.TABLE_LOOKUP in allowed:
        ordered = [RetrievalStrategy.TABLE_LOOKUP] + [
            strategy
            for strategy in allowed
            if strategy != RetrievalStrategy.TABLE_LOOKUP
        ]
        return ordered[: max(policy.max_strategies_per_query - 1, 0)]
    return allowed[: max(policy.max_strategies_per_query - 1, 0)]


def _looks_like_maintenance_interval_query(context: RetrievalContext) -> bool:
    query_text = (
        context.analyzed_query.effective_query()
        if context.analyzed_query is not None
        else context.query_text
    )
    normalized = query_text.lower()
    return mentions_maintenance_interval(normalized)

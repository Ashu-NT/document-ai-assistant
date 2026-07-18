from __future__ import annotations

import re

from src.application.langgraph.reflection.models import RetryPlan
from src.application.langgraph.reflection.strategies.retry_reformulation.retry_reformulation_context import (
    RetryReformulationContext,
)
from src.application.langgraph.retrieval_strategy import StrategyRetryPolicy

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(value: str) -> set[str]:
    return set(_TOKEN_RE.findall((value or "").lower()))


def _is_related(*, original_user_question: str, retry_query: str) -> bool:
    question_tokens = _tokenize(original_user_question)
    retry_tokens = _tokenize(retry_query)
    if not question_tokens or not retry_tokens:
        return False
    overlap = question_tokens.intersection(retry_tokens)
    return len(overlap) >= min(2, len(question_tokens))


class KeywordExpansionRetryReformulationStrategy:
    """The one reformulation strategy class, shared by the generic default
    and every registered domain intent -- the only thing that differs
    between them is `expansion_terms` (empty for generic). Registered
    against multiple intents rather than duplicated into near-identical
    per-intent classes.

    Query-text behavior is unchanged from the former `RetryQueryBuilder`:
    a real, related `reflection_decision.retry_query` is used verbatim;
    only the fallback path (no retry_query, or an unrelated one) appends
    `expansion_terms` and `missing_information`. The strategy hint is new:
    every call also asks `StrategyRetryPolicy` for a recommended retrieval
    strategy, carried on the same `RetryPlan` instead of being computed
    separately by the caller.
    """

    def __init__(
        self,
        *,
        expansion_terms: tuple[str, ...] = (),
        strategy_retry_policy: StrategyRetryPolicy | None = None,
    ) -> None:
        self._expansion_terms = expansion_terms
        self._strategy_retry_policy = strategy_retry_policy or StrategyRetryPolicy()

    def build_retry_plan(self, context: RetryReformulationContext) -> RetryPlan:
        decision = context.reflection_decision
        retry_query = decision.retry_query
        if retry_query and _is_related(
            original_user_question=context.original_user_question,
            retry_query=retry_query,
        ):
            final_query = retry_query
        else:
            final_query = self._fallback_query(
                original_user_question=context.original_user_question,
                missing_information=decision.missing_information,
            )

        recommended_strategies = self._strategy_retry_policy.recommend(
            retry_reason=decision.reason,
            retry_query=final_query,
            initial_primary_strategy=context.current_primary_strategy,
        )

        return RetryPlan(
            retry_query=final_query,
            document_id=context.selected_document_id,
            top_k=context.top_k,
            reason=decision.reason,
            retrieval_strategy_hint=(
                recommended_strategies[0] if recommended_strategies else None
            ),
            secondary_strategy_hints=list(recommended_strategies[1:]),
        )

    def _fallback_query(
        self,
        *,
        original_user_question: str,
        missing_information: list[str],
    ) -> str:
        parts = [
            original_user_question.strip(),
            *self._expansion_terms,
            *(item for item in missing_information if item),
        ]
        return " ".join(dict.fromkeys(" ".join(parts).split()))

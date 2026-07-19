from __future__ import annotations

from src.application.langgraph.retrieval_strategy.constants.retrieval_strategy_constants import (
    MULTI_PRIMARY_STRATEGIES,
    SIGNAL_CATEGORY_TO_STRATEGY,
)
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
    RetrievalStrategyDecision,
    RetrievalStrategySignal,
)
from src.application.langgraph.retrieval_strategy.policies import (
    RetrievalStrategyPolicy,
    StrategyPriorityPolicy,
)
from src.application.langgraph.retrieval_strategy.selectors.strategy_confidence_scorer import (
    score_confidence,
)
from src.application.langgraph.retrieval_strategy.selectors.strategy_secondary_selector import (
    select_secondary_strategies,
)


class DeterministicStrategySelector:
    def __init__(
        self,
        *,
        priority_policy: StrategyPriorityPolicy | None = None,
    ) -> None:
        self.priority_policy = priority_policy or StrategyPriorityPolicy()

    def select(
        self,
        *,
        context: RetrievalContext,
        signals: list[RetrievalStrategySignal],
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalStrategyDecision:
        if context.requested_strategy is not None:
            return RetrievalStrategyDecision(
                primary_strategy=context.requested_strategy,
                secondary_strategies=list(context.requested_secondary_strategies),
                confidence=1.0,
                reason="Retrieval strategy was explicitly requested by the caller.",
                signals=signals,
                requires_document=False,
                document_id=context.effective_document_id,
                query=context.query_text,
                rewritten_query=(
                    context.analyzed_query.effective_query()
                    if context.analyzed_query is not None
                    else None
                ),
                top_k=min(context.top_k or policy.default_top_k, policy.max_top_k),
                use_llm_selector=False,
                diagnostics={"selector": "deterministic", "forced": True},
            )

        if context.route == "document_exploration":
            return RetrievalStrategyDecision(
                primary_strategy=RetrievalStrategy.DOCUMENT_EXPLORATION,
                confidence=0.95,
                reason="Route already indicates document exploration.",
                signals=signals,
                requires_document=True,
                document_id=context.effective_document_id,
                query=context.query_text,
                rewritten_query=(
                    context.analyzed_query.effective_query()
                    if context.analyzed_query is not None
                    else None
                ),
                top_k=min(context.top_k or policy.default_top_k, policy.max_top_k),
                diagnostics={"selector": "deterministic", "route": context.route},
            )

        scores = self._score_strategies(signals)
        ranked = self._rank_strategies(scores)
        if not ranked:
            return self._fallback_decision(context=context, policy=policy, signals=signals)

        strong = [strategy for strategy in ranked if scores[strategy] >= 4.0]
        has_multi_signal = any(signal.category == "multi" for signal in signals)

        strong_multi_candidates = [
            strategy for strategy in strong if strategy in MULTI_PRIMARY_STRATEGIES
        ]
        if (
            has_multi_signal
            and policy.allow_multi_strategy
            and len(strong_multi_candidates) >= 2
        ):
            selected = strong_multi_candidates[: policy.max_strategies_per_query]
            return self._build_decision(
                primary_strategy=RetrievalStrategy.MULTI_STRATEGY,
                secondary_strategies=selected,
                confidence=score_confidence(scores, selected[0]),
                reason="The query contains multiple retrieval intents that should be executed together.",
                context=context,
                policy=policy,
                signals=signals,
                diagnostics={"selector": "deterministic", "mode": "multi"},
            )

        primary = ranked[0]
        secondary = select_secondary_strategies(
            context=context,
            ranked=ranked,
            scores=scores,
            primary=primary,
            policy=policy,
        )
        return self._build_decision(
            primary_strategy=primary,
            secondary_strategies=secondary,
            confidence=score_confidence(scores, primary),
            reason=self._reason(primary, secondary, signals),
            context=context,
            policy=policy,
            signals=signals,
            diagnostics={
                "selector": "deterministic",
                "strategy_scores": {
                    strategy.value: scores[strategy]
                    for strategy in ranked
                },
            },
        )

    @staticmethod
    def _score_strategies(
        signals: list[RetrievalStrategySignal],
    ) -> dict[RetrievalStrategy, float]:
        scores: dict[RetrievalStrategy, float] = {}
        for signal in signals:
            strategy = SIGNAL_CATEGORY_TO_STRATEGY.get(signal.category)
            if strategy is None:
                continue
            scores[strategy] = scores.get(strategy, 0.0) + signal.score
        return scores

    def _rank_strategies(
        self,
        scores: dict[RetrievalStrategy, float],
    ) -> list[RetrievalStrategy]:
        if not scores:
            return []
        priority = {
            strategy: index
            for index, strategy in enumerate(self.priority_policy.ordered_strategies)
        }
        ranked = sorted(
            scores.items(),
            key=lambda item: (-item[1], priority.get(item[0], len(priority))),
        )
        return [strategy for strategy, score in ranked if score > 0]

    def _build_decision(
        self,
        *,
        primary_strategy: RetrievalStrategy,
        secondary_strategies: list[RetrievalStrategy],
        confidence: float,
        reason: str,
        context: RetrievalContext,
        policy: RetrievalStrategyPolicy,
        signals: list[RetrievalStrategySignal],
        diagnostics: dict[str, object],
    ) -> RetrievalStrategyDecision:
        return RetrievalStrategyDecision(
            primary_strategy=primary_strategy,
            secondary_strategies=secondary_strategies,
            confidence=confidence,
            reason=reason,
            signals=signals,
            requires_document=False,
            document_id=context.effective_document_id,
            query=context.query_text,
            rewritten_query=(
                context.analyzed_query.effective_query()
                if context.analyzed_query is not None
                else None
            ),
            top_k=min(context.top_k or policy.default_top_k, policy.max_top_k),
            use_llm_selector=False,
            diagnostics=diagnostics,
        )

    def _fallback_decision(
        self,
        *,
        context: RetrievalContext,
        policy: RetrievalStrategyPolicy,
        signals: list[RetrievalStrategySignal],
    ) -> RetrievalStrategyDecision:
        return RetrievalStrategyDecision(
            primary_strategy=policy.default_strategy,
            confidence=0.60,
            reason="No strong deterministic retrieval-strategy signals were detected.",
            signals=signals,
            document_id=context.effective_document_id,
            query=context.query_text,
            rewritten_query=(
                context.analyzed_query.effective_query()
                if context.analyzed_query is not None
                else None
            ),
            top_k=min(context.top_k or policy.default_top_k, policy.max_top_k),
            diagnostics={"selector": "deterministic", "fallback": True},
        )

    @staticmethod
    def _reason(
        primary: RetrievalStrategy,
        secondary: list[RetrievalStrategy],
        signals: list[RetrievalStrategySignal],
    ) -> str:
        matched = ", ".join(signal.value for signal in signals[:3]) or "generic wording"
        if secondary:
            return (
                f"Primary strategy {primary.value} was selected with supporting "
                f"secondary strategies {[item.value for item in secondary]}. Signals: {matched}."
            )
        return f"Primary strategy {primary.value} was selected from signals: {matched}."

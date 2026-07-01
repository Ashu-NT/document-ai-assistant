from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from src.application.langgraph.routing import RouteDecision, RouteType
from src.application.langgraph.strategy_advisor.advisor_models import StrategyAdvisorProposal
from src.application.langgraph.strategy_advisor.strategy_reason_builder import (
    StrategyReasonBuilder,
)

if TYPE_CHECKING:
    from src.application.langgraph.retrieval_strategy.policies import (
        RetrievalStrategyPolicy,
    )
    from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
        RetrievalStrategy,
    )
    from src.application.langgraph.retrieval_strategy.models.retrieval_strategy_decision import (
        RetrievalStrategyDecision,
    )

_ROUTE_LOCKED_TYPES = {
    RouteType.BLOCKED_ACTION,
    RouteType.OUT_OF_SCOPE,
    RouteType.LIST_DOCUMENTS,
    RouteType.SELECT_DOCUMENT,
    RouteType.CURRENT_DOCUMENT,
    RouteType.CLEAR_DOCUMENT,
    RouteType.HELP,
    RouteType.EXIT,
    RouteType.CLARIFICATION_RESPONSE,
    RouteType.FIND_DOCUMENT,
    RouteType.DOCUMENT_DETAILS,
    RouteType.RETRIEVAL_TRACE,
    RouteType.QUALITY_GATE,
}


class StrategyDecisionMerger:
    def __init__(
        self,
        *,
        reason_builder: StrategyReasonBuilder | None = None,
    ) -> None:
        self.reason_builder = reason_builder or StrategyReasonBuilder()

    def merge_retrieval_decision(
        self,
        *,
        deterministic_decision: RetrievalStrategyDecision,
        proposal: StrategyAdvisorProposal,
        query_text: str,
        policy: RetrievalStrategyPolicy,
    ) -> RetrievalStrategyDecision:
        from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
            RetrievalStrategy,
        )
        from src.application.langgraph.retrieval_strategy.models.retrieval_strategy_decision import (
            RetrievalStrategyDecision,
        )

        deterministic = deterministic_decision.selected_strategies
        merged: list[RetrievalStrategy] = list(deterministic)
        for strategy in proposal.recommended_strategies:
            if strategy not in merged:
                merged.append(strategy)
        if (
            proposal.requires_table
            and any(strategy in _table_support_strategies() for strategy in merged)
            and RetrievalStrategy.TABLE_LOOKUP not in merged
        ):
            merged.append(RetrievalStrategy.TABLE_LOOKUP)
        max_count = max(policy.max_strategies_per_query, 1)
        merged = merged[:max_count]
        if len(merged) <= 1 or not policy.allow_multi_strategy:
            primary = merged[0] if merged else deterministic_decision.primary_strategy
            secondary: list[RetrievalStrategy] = []
        else:
            primary = RetrievalStrategy.MULTI_STRATEGY
            secondary = merged
        merged_names = [strategy.value for strategy in merged]
        diagnostics = {
            **dict(deterministic_decision.diagnostics),
            "advisor_intent": proposal.intent.value,
            "advisor_route": proposal.route,
            "advisor_comparison": proposal.comparison,
            "advisor_requires_table": proposal.requires_table,
            "advisor_concepts": list(proposal.concepts),
            "advisor_added_strategies": [
                strategy.value
                for strategy in merged
                if strategy not in deterministic
            ],
            "advisor_accepted": True,
        }
        return RetrievalStrategyDecision(
            primary_strategy=primary,
            secondary_strategies=secondary,
            confidence=max(deterministic_decision.confidence, proposal.confidence),
            reason=self.reason_builder.build_merge_reason(
                query_text=query_text,
                deterministic_reason=deterministic_decision.reason,
                proposal=proposal,
                merged_strategy_names=merged_names,
            ),
            signals=list(deterministic_decision.signals),
            requires_document=deterministic_decision.requires_document,
            document_id=deterministic_decision.document_id,
            query=deterministic_decision.query,
            rewritten_query=deterministic_decision.rewritten_query,
            top_k=deterministic_decision.top_k,
            use_llm_selector=deterministic_decision.use_llm_selector,
            diagnostics=diagnostics,
        )

    def merge_route_decision(
        self,
        *,
        deterministic_decision: RouteDecision,
        proposal: StrategyAdvisorProposal,
        deep_research_enabled: bool,
    ) -> tuple[RouteDecision, bool, str | None]:
        if deterministic_decision.route_type in _ROUTE_LOCKED_TYPES:
            return deterministic_decision, False, "route_locked"
        if proposal.route == deterministic_decision.route_type.value:
            return deterministic_decision, False, None
        if (
            proposal.route == RouteType.DEEP_RESEARCH.value
            and deterministic_decision.route_type == RouteType.ANSWER_QUESTION
            and deep_research_enabled
        ):
            upgraded = replace(
                deterministic_decision,
                route_type=RouteType.DEEP_RESEARCH,
                confidence=max(
                    deterministic_decision.confidence,
                    proposal.confidence,
                ),
                reason=(
                    "The guarded advisor detected a comparison or multi-concept "
                    "research request and safely upgraded the route to deep research."
                ),
                requires_document=True,
                is_compound=True,
            )
            return upgraded, True, None
        return deterministic_decision, False, "deterministic_route_retained"


def _table_support_strategies() -> set[RetrievalStrategy]:
    from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
        RetrievalStrategy,
    )

    return {
        RetrievalStrategy.MAINTENANCE_LOOKUP,
        RetrievalStrategy.PROCEDURE_LOOKUP,
        RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
        RetrievalStrategy.TECHNICAL_SPECIFICATION,
        RetrievalStrategy.CERTIFICATION_LOOKUP,
    }

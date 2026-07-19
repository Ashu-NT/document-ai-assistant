from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    deduplicate_identifiers,
    extract_identifiers_from_step_results,
)
from src.application.langgraph.nodes.question_answering.retry_retrieval_node_helpers import (
    extract_answer_intent,
)
from src.application.langgraph.reflection.models.retry_plan import RetryPlan
from src.application.langgraph.retrieval_strategy import (
    RetrievalContext,
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
)
from src.application.langgraph.retrieval_strategy.services.retrieval_strategy_state_adapter import (
    advisor_proposal_from_state,
    execution_result_to_tool_result,
    requested_strategy_from_state,
    strategy_patch as build_strategy_patch,
)
from src.application.langgraph.state import AgentState


@dataclass(slots=True)
class RetryStrategyExecutionOutcome:
    retry_result: Any | None = None
    resolved_identifiers: list = field(default_factory=list)
    strategy_patch: dict[str, object] = field(default_factory=dict)


def execute_retry_strategy_plan(
    *,
    state: AgentState,
    retry_query: str,
    retry_top_k: int,
    reason: str,
    retry_plan: RetryPlan,
    resolved_identifiers: list,
    tool_registry: ToolRegistry,
    retrieval_strategy_policy: RetrievalStrategyPolicy,
    retrieval_strategy_service: RetrievalStrategyService | None,
    retrieval_plan_executor: RetrievalPlanExecutor | None,
) -> RetryStrategyExecutionOutcome:
    """Selects and executes a retrieval-strategy plan for a retry, using
    `retry_plan`'s own recommendation (unless the caller explicitly forced a
    strategy) -- unless disabled, or the collaborators aren't wired in, in
    which case the caller falls back to a plain `retrieve_chunks` call."""
    outcome = RetryStrategyExecutionOutcome(resolved_identifiers=resolved_identifiers)
    if not (
        state.get("retrieval_strategy_enabled")
        and retrieval_strategy_policy.enabled
        and retrieval_strategy_service is not None
        and retrieval_plan_executor is not None
    ):
        return outcome

    # An explicit caller-forced strategy (e.g. a CLI override) always wins
    # over retry_plan's own recommendation.
    state_forced_strategy = requested_strategy_from_state(state)
    if state_forced_strategy is not None:
        requested_strategy = state_forced_strategy
        requested_secondary_strategies: list = []
    else:
        requested_strategy = retry_plan.retrieval_strategy_hint
        requested_secondary_strategies = retry_plan.secondary_strategy_hints

    strategy_context = RetrievalContext(
        query_text=retry_query,
        route=state.get("route"),
        document_id=state.get("selected_document_id") or state.get("document_id"),
        selected_document_id=state.get("selected_document_id"),
        document_title=state.get("document_title"),
        selected_document_title=state.get("selected_document_title"),
        top_k=retry_top_k,
        answer_intent=extract_answer_intent(state),
        retry_reason=reason,
        retry_query=retry_query,
        requested_strategy=requested_strategy,
        requested_secondary_strategies=requested_secondary_strategies,
        use_llm_selector=bool(state.get("llm_retrieval_strategy_enabled")),
        strategy_advisor_proposal=advisor_proposal_from_state(state),
    )
    try:
        strategy_result = retrieval_strategy_service.select_and_plan(
            strategy_context,
            tool_registry=tool_registry,
        )
        execution_result = retrieval_plan_executor.execute(
            strategy_result.plan,
            tool_registry=tool_registry,
            max_chunks=retrieval_strategy_policy.max_merged_chunks,
        )
        outcome.strategy_patch = build_strategy_patch(
            strategy_result=strategy_result,
            execution_result=execution_result,
        )
        outcome.resolved_identifiers = deduplicate_identifiers(
            [
                *resolved_identifiers,
                *extract_identifiers_from_step_results(execution_result.step_results),
            ]
        )
        outcome.retry_result = execution_result_to_tool_result(
            execution_result,
            tool_name="retry_retrieval",
            description="LangGraph retrieval-strategy retry execution result.",
            success_message="Retry evidence retrieved successfully.",
            failure_message="Retry retrieval strategy execution failed.",
        )
    except Exception as exc:
        outcome.strategy_patch = {"retrieval_strategy_errors": [str(exc)]}
    return outcome

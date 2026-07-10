from __future__ import annotations

from dataclasses import asdict

from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.retrieval_strategy.constants import (
    CLI_RETRIEVAL_STRATEGY_ALIASES,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.strategy_advisor.advisor_models import (
    StrategyAdvisorProposal,
)
from src.domain.retrieval.citation import Citation

# Shared by answer_question_node.py, retry_retrieval_node.py,
# retrieve_evidence_node.py, and (partially) create_research_plan_node.py --
# these four `AgentState` -> retrieval-strategy adapters were previously
# hand-copied into each node module.


def requested_strategy_from_state(state: AgentState):
    raw_value = state.get("requested_retrieval_strategy")
    if not isinstance(raw_value, str) or not raw_value:
        return None
    return CLI_RETRIEVAL_STRATEGY_ALIASES.get(raw_value.strip().lower())


def advisor_proposal_from_state(state: AgentState) -> StrategyAdvisorProposal | None:
    payload = state.get("strategy_advisor_result")
    if not isinstance(payload, dict):
        return None
    proposal = payload.get("proposal")
    if not isinstance(proposal, dict):
        return None
    return StrategyAdvisorProposal.from_dict(proposal)


def strategy_patch(
    *,
    strategy_result,
    execution_result,
) -> dict[str, object]:
    decision = strategy_result.decision
    return {
        "retrieval_strategy_decision": serialize_graph_value(asdict(decision)),
        "retrieval_plan": serialize_graph_value(strategy_result.plan.to_dict()),
        "retrieval_execution_result": serialize_graph_value(
            execution_result.to_dict()
        ),
        "retrieval_strategy_trace": serialize_graph_value(asdict(strategy_result.trace)),
        "selected_retrieval_strategies": [
            strategy.value for strategy in decision.selected_strategies
        ],
        "retrieval_strategy_errors": list(execution_result.errors),
    }


def execution_result_to_tool_result(
    execution_result,
    *,
    tool_name: str,
    description: str,
    success_message: str,
    failure_message: str,
    include_execution_diagnostics: bool = False,
):
    """Build a `ToolResult` from a `RetrievalExecutionResult`.

    `include_execution_diagnostics` preserves a real behavioral difference
    between the two original call sites: `retrieve_evidence_node.py` added
    `tool_names`/`strategy_count` to the diagnostics payload,
    `retry_retrieval_node.py` did not. Both existing behaviors are kept via
    this flag rather than picking one.
    """
    from src.application.tools.common import ToolMetadata, ToolResult

    citations = [
        chunk.citation
        for chunk in execution_result.evidence_chunks
        if isinstance(chunk.citation, Citation)
    ]
    diagnostics = dict(execution_result.diagnostics)
    if include_execution_diagnostics:
        diagnostics = {
            **diagnostics,
            "tool_names": list(execution_result.tool_names),
            "strategy_count": len(execution_result.plan.steps),
        }
    metadata = ToolMetadata(
        tool_name=tool_name,
        category="retrieval",
        description=description,
        mutates_state=False,
        supports_trace=True,
    )
    return ToolResult(
        success=execution_result.success,
        message=success_message if execution_result.success else failure_message,
        data={
            "chunks": execution_result.evidence_chunks,
            "context_chunks": execution_result.evidence_chunks,
            "citations": citations,
            "retrieval_execution_result": execution_result,
        },
        error_code=(
            None
            if execution_result.success
            else execution_result.errors[0]
            if execution_result.errors
            else "retrieval_strategy_failed"
        ),
        diagnostics=diagnostics,
        metadata=metadata,
    )

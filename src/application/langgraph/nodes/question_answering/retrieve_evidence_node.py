from __future__ import annotations

from dataclasses import asdict

from src.application.langgraph.common import GraphError
from src.application.langgraph.common import serialize_graph_value
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    extend_trace,
    resolve_selected_document,
    serialize_tool_result,
)
from src.application.langgraph.retrieval_strategy import (
    CLI_RETRIEVAL_STRATEGY_ALIASES,
    RetrievalContext,
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.retrieval import RetrieveChunksRequest
from src.domain.retrieval.citation import Citation


class RetrieveEvidenceNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        retrieval_strategy_service: RetrievalStrategyService | None = None,
        retrieval_plan_executor: RetrievalPlanExecutor | None = None,
        retrieval_strategy_policy: RetrievalStrategyPolicy | None = None,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.retrieval_strategy_service = retrieval_strategy_service
        self.retrieval_plan_executor = retrieval_plan_executor
        self.retrieval_strategy_policy = (
            retrieval_strategy_policy or RetrievalStrategyPolicy()
        )
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "retrieve_evidence",
            route=state.get("route"),
            tool_name="retrieve_chunks",
        )
        try:
            tool = self.tool_registry.require("retrieve_chunks")
        except GraphError as exc:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code=exc.error_code,
                diagnostics=exc.details,
            )
            return {
                "error": build_error(
                    message=exc.message,
                    error_code=exc.error_code,
                    diagnostics=exc.details,
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        query_text = state.get("question") or state["user_input"].strip()
        resolved_document_id, _ = resolve_selected_document(state)
        strategy_patch: dict[str, object] = {}
        result = None
        if (
            state.get("retrieval_strategy_enabled")
            and self.retrieval_strategy_policy.enabled
            and self.retrieval_strategy_service is not None
            and self.retrieval_plan_executor is not None
        ):
            strategy_context = RetrievalContext(
                query_text=query_text,
                route=state.get("route"),
                document_id=resolved_document_id,
                selected_document_id=state.get("selected_document_id"),
                document_title=state.get("document_title"),
                selected_document_title=state.get("selected_document_title"),
                top_k=state.get("top_k") or self.retrieval_strategy_policy.default_top_k,
                requested_strategy=_requested_strategy_from_state(state),
                use_llm_selector=bool(state.get("llm_retrieval_strategy_enabled")),
            )
            try:
                strategy_result = self.retrieval_strategy_service.select_and_plan(
                    strategy_context,
                    tool_registry=self.tool_registry,
                )
                execution_result = self.retrieval_plan_executor.execute(
                    strategy_result.plan,
                    tool_registry=self.tool_registry,
                    max_chunks=self.retrieval_strategy_policy.max_merged_chunks,
                )
                strategy_patch = _strategy_patch(
                    strategy_result=strategy_result,
                    execution_result=execution_result,
                )
                result = _execution_result_to_tool_result(execution_result)
            except Exception as exc:
                strategy_patch = {
                    "retrieval_strategy_errors": [str(exc)],
                }

        if result is None:
            result = tool.run(
                RetrieveChunksRequest(
                    query_text=query_text,
                    document_id=resolved_document_id,
                    top_k=state.get("top_k") or 5,
                )
            )
        tool_results = dict(state["tool_results"])
        tool_results["retrieve_evidence"] = serialize_tool_result(result)
        trace_entry = self.recorder.finish_node(
            token,
            success=result.success,
            error_code=result.error_code,
            diagnostics={
                **dict(result.diagnostics or {}),
                "retrieval_strategy": strategy_patch.get("retrieval_strategy_decision"),
            },
        )
        patch = {
            "tool_results": tool_results,
            "trace": extend_trace(state["trace"], trace_entry),
            **strategy_patch,
        }
        if result.success:
            data = result.data or {}
            chunk_count = len(data.get("chunks", []))
            context_count = len(data.get("context_chunks", []))
            patch["response_text"] = (
                f"Retrieved {chunk_count} evidence chunk(s); "
                f"{context_count} chunk(s) after context assembly."
            )
            return patch

        patch["error"] = build_error(
            message=result.message or "Evidence retrieval failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch


def _requested_strategy_from_state(state: AgentState):
    raw_value = state.get("requested_retrieval_strategy")
    if not isinstance(raw_value, str) or not raw_value:
        return None
    return CLI_RETRIEVAL_STRATEGY_ALIASES.get(raw_value.strip().lower())


def _strategy_patch(
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


def _execution_result_to_tool_result(execution_result):
    from src.application.tools.common import ToolMetadata, ToolResult

    citations = [
        chunk.citation
        for chunk in execution_result.evidence_chunks
        if isinstance(chunk.citation, Citation)
    ]
    diagnostics = {
        **dict(execution_result.diagnostics),
        "tool_names": list(execution_result.tool_names),
        "strategy_count": len(execution_result.plan.steps),
    }
    metadata = ToolMetadata(
        tool_name="retrieve_evidence",
        category="retrieval",
        description="LangGraph retrieval-strategy execution result.",
        mutates_state=False,
        supports_trace=True,
    )
    return ToolResult(
        success=execution_result.success,
        message=(
            "Evidence retrieved successfully."
            if execution_result.success
            else "Retrieval strategy execution failed."
        ),
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

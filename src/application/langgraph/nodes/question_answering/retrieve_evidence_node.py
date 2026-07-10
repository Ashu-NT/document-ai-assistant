from __future__ import annotations

from src.application.langgraph.common import GraphError
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    extend_trace,
    resolve_selected_document,
    serialize_tool_result,
)
from src.application.langgraph.retrieval_strategy import (
    RetrievalContext,
    RetrievalPlanExecutor,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
    advisor_proposal_from_state,
    execution_result_to_tool_result,
    requested_strategy_from_state,
    strategy_patch as build_strategy_patch,
)
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.retrieval import RetrieveChunksRequest


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
                requested_strategy=requested_strategy_from_state(state),
                use_llm_selector=bool(state.get("llm_retrieval_strategy_enabled")),
                strategy_advisor_proposal=advisor_proposal_from_state(state),
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
                strategy_patch = build_strategy_patch(
                    strategy_result=strategy_result,
                    execution_result=execution_result,
                )
                result = execution_result_to_tool_result(
                    execution_result,
                    tool_name="retrieve_evidence",
                    description="LangGraph retrieval-strategy execution result.",
                    success_message="Evidence retrieved successfully.",
                    failure_message="Retrieval strategy execution failed.",
                    include_execution_diagnostics=True,
                )
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

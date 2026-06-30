from __future__ import annotations

from typing import Any

from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import build_error, extend_trace
from src.application.langgraph.research import ResearchService
from src.application.langgraph.research.services import ResearchStateMapper
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class ExecuteResearchNode:
    def __init__(
        self,
        research_service: ResearchService,
        tool_registry: ToolRegistry,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.research_service = research_service
        self.tool_registry = tool_registry
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict[str, Any]:
        token = self.recorder.start_node(
            "execute_research",
            route=state.get("route"),
            selected_document_id=state.get("selected_document_id"),
        )
        plan = ResearchStateMapper.plan_from_dict(state.get("research_plan"))
        if plan is None:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="research_plan_missing",
            )
            return {
                "error": build_error(
                    message="Research execution could not start because no research plan was available.",
                    error_code="research_plan_missing",
                ),
                "trace": extend_trace(state["trace"], trace_entry),
            }

        current_result = ResearchStateMapper.result_from_state(state)
        result = self.research_service.execute_research(
            plan=plan,
            tool_registry=self.tool_registry,
            current_result=current_result,
            use_llm_strategy=bool(state.get("llm_retrieval_strategy_enabled", False)),
        )
        research_trace = dict(state.get("research_trace") or {})
        research_trace["task_tool_names"] = {
            task_result.task_id: list(task_result.tool_names)
            for task_result in result.task_results
        }
        research_trace["retrieval_strategies_per_task"] = {
            task_result.task_id: task_result.retrieval_strategy or ""
            for task_result in result.task_results
        }
        research_trace["evidence_counts_per_task"] = {
            task_result.task_id: len(task_result.evidence)
            for task_result in result.task_results
        }
        trace_entry = self.recorder.finish_node(
            token,
            success=True,
            diagnostics={
                "task_result_count": len(result.task_results),
                "evidence_count": len(result.evidence),
                "research_success": result.success,
            },
        )
        return {
            **ResearchStateMapper.result_to_state(result),
            "research_trace": research_trace,
            "research_followup_pending": False,
            "trace": extend_trace(state["trace"], trace_entry),
        }

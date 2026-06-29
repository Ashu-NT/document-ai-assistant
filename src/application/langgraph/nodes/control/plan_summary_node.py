from __future__ import annotations

from typing import Any

from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


class PlanSummaryNode:
    def __init__(self, *, recorder: GraphRunRecorder | None = None) -> None:
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        execution_plan = state.get("execution_plan") or {}
        trace_token = self.recorder.start_node(
            "plan_summary",
            route=state.get("route"),
            plan_id=_string_value(execution_plan.get("plan_id")),
            plan_goal=_string_value(execution_plan.get("goal")),
            selected_document_id=state.get("selected_document_id"),
        )
        answer_text = self._build_response_text(state)
        trace_entry = self.recorder.finish_node(
            trace_token,
            success=state.get("error") is None,
            diagnostics={
                "show_plan": bool(state.get("show_plan")),
                "step_count": len(state.get("plan_steps", [])),
            },
        )
        return {
            "response_text": answer_text,
            "trace": extend_trace(state["trace"], trace_entry),
        }

    def _build_response_text(self, state: AgentState) -> str:
        answer_text = (
            _string_value(state.get("response_text"))
            or _string_value((state.get("plan_results") or {}).get("final_response_text"))
            or "Planned task completed."
        )
        if not state.get("show_plan"):
            return answer_text

        plan_lines = ["Plan", "----"]
        for index, step in enumerate(state.get("plan_steps", []), start=1):
            if not isinstance(step, dict):
                continue
            description = _string_value(step.get("description")) or _string_value(
                step.get("tool_name")
            )
            plan_lines.append(f"{index}. {description}")
        if len(plan_lines) == 2:
            plan_lines.append("No multi-step plan was used.")

        answer_lines = ["", "Answer", "------", answer_text]
        return "\n".join([*plan_lines, *answer_lines]).strip()


def _string_value(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None

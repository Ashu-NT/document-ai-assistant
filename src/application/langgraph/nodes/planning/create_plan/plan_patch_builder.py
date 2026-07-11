from __future__ import annotations

from typing import Any

from src.application.langgraph.nodes.node_utils import extend_trace
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder


def build_accepted_plan_patch(
    *,
    state: AgentState,
    recorder: GraphRunRecorder,
    token,
    plan,
    planning_source: str,
    planning_warnings: list[str],
    raw_llm_plan: str | None,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    trace_entry = recorder.finish_node(
        token,
        success=True,
        diagnostics={
            "plan_id": plan.plan_id,
            "plan_goal": plan.goal,
            "step_count": plan.step_count,
            "requires_document": plan.requires_document,
            "plan_kind": plan.diagnostics.get("plan_kind"),
            "planning_source": planning_source,
            **diagnostics,
        },
    )
    patch: dict[str, object] = {
        "execution_plan": plan.to_dict(),
        "validated_plan": plan.to_dict(),
        "plan_steps": [step.to_dict() for step in plan.steps],
        "plan_results": {
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "plan_success": None,
            "step_outputs": {},
            "plan_kind": plan.diagnostics.get("plan_kind"),
        },
        "planning_source": planning_source,
        "planning_errors": [],
        "planning_warnings": planning_warnings,
        "raw_llm_plan": raw_llm_plan if state.get("show_raw_plan") else None,
        "trace": extend_trace(state["trace"], trace_entry),
    }
    if plan.requires_document and not (
        state.get("document_id")
        or state.get("selected_document_id")
        or state.get("document_query")
        or plan.document_id
    ):
        patch.update(
            {
                "needs_clarification": True,
                "clarification_message": (
                    "This multi-step request needs a document. "
                    "Please select one first or pass --document."
                ),
                "clarification_question": "Which document should I use?",
                "response_text": (
                    "This multi-step request needs a document. "
                    "Please select one first or pass --document."
                ),
            }
        )
    return patch


def build_failed_plan_patch(
    *,
    state: AgentState,
    recorder: GraphRunRecorder,
    token,
    raw_llm_plan: str,
    deterministic_confidence: float,
    errors: list[str],
    warnings: list[str],
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    response_text = (
        "I could not build a safe multi-step plan for that request. "
        "Please narrow the request or specify the document to use."
    )
    if _needs_document_clarification(state):
        response_text = (
            "I could not safely build a multi-step plan without a document. "
            "Please select a document first or pass --document."
        )
    trace_entry = recorder.finish_node(
        token,
        success=False,
        error_code="plan_validation_failed",
        diagnostics={
            "planning_source": "failed",
            "deterministic_attempted": True,
            "deterministic_confidence": deterministic_confidence,
            "error_count": len(errors),
            "warning_count": len(warnings),
            **diagnostics,
        },
    )
    patch: dict[str, Any] = {
        "execution_plan": None,
        "validated_plan": None,
        "plan_steps": [],
        "planning_source": "failed",
        "planning_errors": [error for error in errors if error],
        "planning_warnings": [warning for warning in warnings if warning],
        "raw_llm_plan": raw_llm_plan if state.get("show_raw_plan") else None,
        "trace": extend_trace(state["trace"], trace_entry),
    }
    if _needs_document_clarification(state):
        patch.update(
            {
                "needs_clarification": True,
                "clarification_message": response_text,
                "clarification_question": "Which document should I use?",
                "response_text": response_text,
            }
        )
        return patch

    patch["error"] = {
        "message": response_text,
        "error_code": "plan_validation_failed",
        "diagnostics": {
            "planning_errors": [error for error in errors if error],
            "planning_warnings": [warning for warning in warnings if warning],
        },
    }
    patch["response_text"] = response_text
    return patch


def _needs_document_clarification(state: AgentState) -> bool:
    return not (
        state.get("document_id")
        or state.get("selected_document_id")
        or state.get("document_query")
    )

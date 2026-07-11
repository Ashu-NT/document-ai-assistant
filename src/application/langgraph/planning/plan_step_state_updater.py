from __future__ import annotations

from typing import Any

from src.application.langgraph.nodes.node_utils import build_error, format_document_options
from src.application.langgraph.state import AgentState
from src.application.tools.common import ToolResult


def store_canonical_tool_result(
    *,
    tool_results: dict[str, Any],
    tool_name: str,
    serialized: dict[str, Any],
) -> None:
    canonical_key = {
        "retrieve_chunks": "retrieve_evidence",
    }.get(tool_name, tool_name)
    tool_results[canonical_key] = serialized


def apply_success_state(
    *,
    next_state: AgentState,
    step,
    result: ToolResult,
    step_outputs: dict[str, dict[str, Any]],
) -> None:
    if not result.success:
        return
    if step.tool_name == "find_document":
        data = result.data or {}
        if isinstance(data, dict):
            title = data.get("display_name") or data.get("title")
            next_state["document_id"] = data.get("document_id")
            next_state["document_title"] = title
            next_state["selected_document_id"] = data.get("document_id")
            next_state["selected_document_title"] = title
            next_state["selected_document_file_name"] = data.get("file_name")
            next_state["needs_clarification"] = False
            next_state["clarification_message"] = None
            next_state["pending_clarification"] = None
            next_state["clarification_options"] = []
            next_state["clarification_question"] = None
            next_state["clarification_candidate_index"] = None
    elif step.tool_name == "format_combined_answer":
        data = result.data or {}
        if isinstance(data, dict):
            next_state["response_text"] = data.get("text")
    elif step.tool_name == "answer_question":
        payload = step_outputs.get(step.output_key, {}).get("data")
        if isinstance(payload, dict):
            next_state["response_text"] = (
                payload.get("answer_text")
                or payload.get("safe_user_message")
                or next_state.get("response_text")
            )


def apply_failure_state(
    *,
    next_state: AgentState,
    step,
    result: ToolResult,
) -> bool:
    if step.tool_name == "find_document":
        if result.error_code == "multiple_documents_found":
            matches = result.diagnostics.get("matches", [])
            next_state["needs_clarification"] = True
            next_state["clarification_options"] = matches if isinstance(matches, list) else []
            next_state["clarification_question"] = (
                "I found multiple matching documents. Which one do you mean?"
            )
            next_state["pending_clarification"] = {
                "kind": "document_selection",
                "route": next_state.get("route"),
            }
            next_state["clarification_message"] = format_document_options(
                next_state["clarification_options"]
            )
            next_state["response_text"] = next_state["clarification_message"]
            return True
        if result.error_code == "document_not_found":
            next_state["needs_clarification"] = True
            next_state["clarification_message"] = (
                "I could not find that document. Please refine the document name or ID."
            )
            next_state["response_text"] = next_state["clarification_message"]
            return True

    next_state["error"] = build_error(
        message=result.message or "Plan step failed.",
        error_code=result.error_code or "tool_failed",
        diagnostics={
            "tool_name": step.tool_name,
            "step_id": step.step_id,
            **dict(result.diagnostics or {}),
        },
    )
    return True

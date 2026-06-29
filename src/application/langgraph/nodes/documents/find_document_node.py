from __future__ import annotations

from src.application.langgraph.common import GraphError
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.nodes.node_utils import (
    build_error,
    extend_trace,
    format_document_options,
    serialize_tool_result,
)
from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.tracing import GraphRunRecorder
from src.application.tools.documents import FindDocumentRequest


class FindDocumentNode:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        recorder: GraphRunRecorder | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.recorder = recorder or GraphRunRecorder()

    def __call__(self, state: AgentState) -> dict:
        token = self.recorder.start_node(
            "find_document",
            route=state.get("route"),
            tool_name="find_document",
        )
        try:
            tool = self.tool_registry.require("find_document")
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

        request = _build_request(state)
        if request is None:
            trace_entry = self.recorder.finish_node(
                token,
                success=False,
                error_code="clarification_required",
            )
            return {
                "needs_clarification": True,
                "clarification_message": "Please specify which document you mean.",
                "trace": extend_trace(state["trace"], trace_entry),
            }

        result = tool.run(request)
        tool_results = dict(state["tool_results"])
        tool_results["find_document"] = serialize_tool_result(result)
        trace_entry = self.recorder.finish_node(
            token,
            success=result.success,
            error_code=result.error_code,
            diagnostics=result.diagnostics,
        )
        patch = {
            "tool_results": tool_results,
            "trace": extend_trace(state["trace"], trace_entry),
        }
        if result.success:
            data = result.data or {}
            if isinstance(data, dict):
                selected_title = data.get("display_name") or data.get("title")
                patch["document_id"] = data.get("document_id")
                patch["document_title"] = selected_title
                patch["selected_document_id"] = data.get("document_id")
                patch["selected_document_title"] = selected_title
                patch["selected_document_file_name"] = data.get("file_name")
                patch["pending_clarification"] = None
                patch["clarification_options"] = []
                patch["clarification_question"] = None
                patch["clarification_candidate_index"] = None
                patch["needs_clarification"] = False
                patch["clarification_message"] = None
                patch["response_text"] = (
                    f"Selected document: {selected_title}."
                    if state.get("route") == RouteType.SELECT_DOCUMENT.value and selected_title
                    else (
                        f"Found document: {selected_title}."
                        if selected_title
                        else "Document resolved."
                    )
                )
            return patch

        if result.error_code in {"multiple_documents_found", "document_not_found"}:
            if result.error_code == "multiple_documents_found":
                matches = _extract_matches(result)
                patch.update(
                    {
                        "needs_clarification": True,
                        "clarification_options": matches,
                        "clarification_question": "I found multiple matching documents. Which one do you mean?",
                        "pending_clarification": {
                            "kind": "document_selection",
                            "route": state.get("route"),
                        },
                        "clarification_message": format_document_options(matches),
                    }
                )
            else:
                patch["needs_clarification"] = True
                patch["clarification_message"] = _clarification_message(result)
            return patch

        patch["error"] = build_error(
            message=result.message or "Document lookup failed.",
            error_code=result.error_code or "tool_failed",
            diagnostics=result.diagnostics,
        )
        return patch


def _build_request(state: AgentState) -> FindDocumentRequest | None:
    if state.get("document_id"):
        return FindDocumentRequest(document_id=state["document_id"])
    if state.get("document_query"):
        return FindDocumentRequest(query_text=state["document_query"])
    return None


def _clarification_message(result) -> str:
    if result.error_code == "multiple_documents_found":
        matches = result.diagnostics.get("matches", [])
        if matches:
            names = ", ".join(match.get("display_name", "?") for match in matches[:5])
            return f"Multiple documents matched your request: {names}. Please be more specific."
        return "Multiple documents matched your request. Please be more specific."
    return "I could not find that document. Please refine the document name or ID."


def _extract_matches(result) -> list[dict]:
    diagnostics = getattr(result, "diagnostics", {}) or {}
    matches = diagnostics.get("matches", [])
    if not isinstance(matches, list):
        return []
    return [match for match in matches if isinstance(match, dict)]

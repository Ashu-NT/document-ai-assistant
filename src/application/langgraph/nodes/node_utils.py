from __future__ import annotations

from typing import Any

from src.application.langgraph.common import serialize_graph_value


def serialize_tool_result(tool_result: Any) -> dict[str, Any]:
    return {
        "success": bool(getattr(tool_result, "success", False)),
        "message": getattr(tool_result, "message", None),
        "error_code": getattr(tool_result, "error_code", None),
        "diagnostics": serialize_graph_value(
            getattr(tool_result, "diagnostics", {}) or {}
        ),
        "metadata": serialize_graph_value(getattr(tool_result, "metadata", None)),
        "data": serialize_graph_value(getattr(tool_result, "data", None)),
    }


def extend_trace(
    existing_trace: list[dict[str, Any]],
    trace_entry: dict[str, Any],
) -> list[dict[str, Any]]:
    return [*existing_trace, trace_entry]


def build_error(
    *,
    message: str,
    error_code: str,
    diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "message": message,
        "error_code": error_code,
        "diagnostics": serialize_graph_value(diagnostics or {}),
    }


def resolve_selected_document(state: dict[str, Any]) -> tuple[str | None, str | None]:
    document_id = state.get("document_id")
    if isinstance(document_id, str) and document_id:
        return document_id, _optional_str(state.get("document_title"))

    selected_document_id = state.get("selected_document_id")
    if isinstance(selected_document_id, str) and selected_document_id:
        return selected_document_id, _optional_str(state.get("selected_document_title"))

    return None, None


def format_document_options(options: list[dict[str, Any]]) -> str:
    if not options:
        return "I could not determine a matching document."

    lines = ["I found multiple matching documents. Which one do you mean?"]
    for index, option in enumerate(options, start=1):
        title = (
            option.get("display_name")
            or option.get("title")
            or option.get("file_name")
            or option.get("document_id")
            or f"Document {index}"
        )
        lines.append(f"{index}. {title}")
    return "\n".join(lines)


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None

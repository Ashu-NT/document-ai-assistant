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

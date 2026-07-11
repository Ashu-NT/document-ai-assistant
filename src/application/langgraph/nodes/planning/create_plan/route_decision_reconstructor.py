from __future__ import annotations

from typing import Any

from src.application.langgraph.routing import RouteDecision, RouteType
from src.application.langgraph.state import AgentState


def reconstruct_route_decision(state: AgentState) -> RouteDecision:
    diagnostics = _route_diagnostics(state)
    route_value = state.get("route") or RouteType.UNKNOWN.value
    try:
        route_type = RouteType(route_value)
    except ValueError:
        route_type = RouteType.UNKNOWN
    return RouteDecision(
        route_type=route_type,
        confidence=_float_value(diagnostics.get("confidence"), default=0.0),
        reason=_string_value(diagnostics.get("reason"))
        or "Reconstructed from routed graph state.",
        extracted_document_query=state.get("document_query"),
        extracted_question=state.get("question"),
        requires_document=bool(diagnostics.get("requires_document", False)),
        uses_current_document=bool(diagnostics.get("uses_current_document", False)),
        is_compound=bool(diagnostics.get("is_compound", False)),
        requires_plan=bool(
            diagnostics.get("requires_plan", route_type == RouteType.PLANNED_TASK)
        ),
        plan_hint=_string_value(diagnostics.get("plan_hint")),
    )


def _route_diagnostics(state: AgentState) -> dict[str, Any]:
    for entry in reversed(list(state.get("trace", []))):
        if not isinstance(entry, dict):
            continue
        if entry.get("node_name") != "route_request":
            continue
        diagnostics = entry.get("diagnostics")
        if isinstance(diagnostics, dict):
            return diagnostics
    return {}


def _float_value(value: object, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _string_value(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None

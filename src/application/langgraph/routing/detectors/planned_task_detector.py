from __future__ import annotations

from src.application.langgraph.routing.route_decision import RouteDecision
from src.application.langgraph.routing.route_input_normalizer import (
    references_current_document,
)
from src.application.langgraph.routing.route_type import RouteType

_PLANNED_COMPARE_MARKERS = ("compare",)
_PLANNED_RETRIEVE_MARKERS = (
    "retrieve evidence",
    "show context",
    "summarize evidence",
)
_PLANNED_EXPLORE_MARKERS = ("explore",)
_PLANNED_LIST_AND_FIND_MARKERS = ("show documents", "list documents")
_PLANNED_FOLLOW_UP_MARKERS = (
    "summarize",
    "answer",
    "maintenance",
    "specification",
    "safety",
    "procedure",
    "troubleshooting",
    "tables",
)


def looks_like_planned_task(value: str) -> bool:
    padded = f" {value} "
    if "compare" in value and " and " in padded:
        return True
    if any(marker in value for marker in _PLANNED_RETRIEVE_MARKERS) and " and " in padded:
        return any(marker in value for marker in _PLANNED_FOLLOW_UP_MARKERS)
    if any(marker in value for marker in _PLANNED_EXPLORE_MARKERS) and " and " in padded:
        return any(marker in value for marker in _PLANNED_FOLLOW_UP_MARKERS)
    if any(marker in value for marker in _PLANNED_LIST_AND_FIND_MARKERS) and any(
        marker in value for marker in ("open ", "find ", "open document ")
    ):
        return True
    return False


def build_planned_task_decision(
    *,
    user_input: str,
    extracted_document_query: str | None,
    normalized_input: str,
) -> RouteDecision:
    return RouteDecision(
        route_type=RouteType.PLANNED_TASK,
        confidence=0.9,
        reason="Detected a deterministic compound request that should use the planning path.",
        extracted_document_query=extracted_document_query,
        extracted_question=user_input.strip(),
        uses_current_document=references_current_document(normalized_input),
        is_compound=True,
        requires_plan=True,
        plan_hint=user_input.strip(),
    )

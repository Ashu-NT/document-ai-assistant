from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.routing.route_type import RouteType


@dataclass(slots=True, frozen=True)
class RouteDecision:
    route_type: RouteType
    confidence: float
    reason: str
    extracted_document_query: str | None = None
    extracted_question: str | None = None
    requires_document: bool = False
    uses_current_document: bool = False
    is_session_command: bool = False
    clarification_candidate_index: int | None = None
    options: dict[str, Any] = field(default_factory=dict)

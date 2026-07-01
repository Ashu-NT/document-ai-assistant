from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
        RetrievalStrategy,
    )


class StrategyAdvisorIntent(StrEnum):
    GENERAL_LOOKUP = "general_lookup"
    COMPARISON = "comparison"
    SUMMARY = "summary"
    CHECKLIST = "checklist"
    REPORT = "report"
    EVIDENCE_REVIEW = "evidence_review"


class StrategyAdvisorStatus(StrEnum):
    SKIPPED = "skipped"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(slots=True)
class StrategyAdvisorRequest:
    query_text: str
    deterministic_route: str | None
    deterministic_route_confidence: float
    deterministic_reason: str
    deterministic_strategies: list[RetrievalStrategy] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    selected_document_id: str | None = None
    selected_document_title: str | None = None
    allowed_routes: list[str] = field(default_factory=list)
    trigger_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_text": self.query_text,
            "deterministic_route": self.deterministic_route,
            "deterministic_route_confidence": self.deterministic_route_confidence,
            "deterministic_reason": self.deterministic_reason,
            "deterministic_strategies": [
                getattr(strategy, "value", str(strategy))
                for strategy in self.deterministic_strategies
            ],
            "signals": list(self.signals),
            "selected_document_id": self.selected_document_id,
            "selected_document_title": self.selected_document_title,
            "allowed_routes": list(self.allowed_routes),
            "trigger_reason": self.trigger_reason,
        }


@dataclass(slots=True)
class StrategyAdvisorProposal:
    intent: StrategyAdvisorIntent
    route: str
    confidence: float
    concepts: list[str]
    recommended_strategies: list[RetrievalStrategy]
    comparison: bool
    requires_table: bool
    reason: str
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent.value,
            "route": self.route,
            "confidence": self.confidence,
            "concepts": list(self.concepts),
            "recommended_strategies": [
                getattr(strategy, "value", str(strategy))
                for strategy in self.recommended_strategies
            ],
            "comparison": self.comparison,
            "requires_table": self.requires_table,
            "reason": self.reason,
            "diagnostics": dict(self.diagnostics),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> StrategyAdvisorProposal | None:
        if not isinstance(payload, dict):
            return None
        try:
            from src.application.langgraph.retrieval_strategy.models.retrieval_strategy import (
                RetrievalStrategy,
            )

            intent = StrategyAdvisorIntent(str(payload.get("intent") or "").strip())
            route = str(payload.get("route") or "").strip()
            concepts = [
                str(item).strip()
                for item in list(payload.get("concepts") or [])
                if str(item).strip()
            ]
            strategies = [
                RetrievalStrategy(str(item).strip())
                for item in list(payload.get("recommended_strategies") or [])
                if str(item).strip()
            ]
            return cls(
                intent=intent,
                route=route,
                confidence=float(payload.get("confidence") or 0.0),
                concepts=concepts,
                recommended_strategies=strategies,
                comparison=bool(payload.get("comparison")),
                requires_table=bool(payload.get("requires_table")),
                reason=str(payload.get("reason") or "").strip(),
                diagnostics=dict(payload.get("diagnostics") or {}),
            )
        except (TypeError, ValueError):
            return None


@dataclass(slots=True)
class StrategyAdvisorEvent:
    name: str
    message: str
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "message": self.message,
            "diagnostics": dict(self.diagnostics),
        }


@dataclass(slots=True)
class StrategyAdvisorOutcome:
    status: StrategyAdvisorStatus
    proposal: StrategyAdvisorProposal | None = None
    reason: str | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)
    events: list[StrategyAdvisorEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "proposal": self.proposal.to_dict() if self.proposal is not None else None,
            "reason": self.reason,
            "diagnostics": dict(self.diagnostics),
            "events": [event.to_dict() for event in self.events],
        }

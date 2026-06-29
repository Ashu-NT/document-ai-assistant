from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class AgentTurnResult:
    user_input: str
    route: str | None
    success: bool
    response_text: str | None
    selected_document_id: str | None
    selected_document_title: str | None
    tool_names: list[str] = field(default_factory=list)
    plan_tool_names: list[str] = field(default_factory=list)
    context_document_ids: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AgentCaseResult:
    case_id: str
    name: str
    passed: bool
    failed_checks: list[str] = field(default_factory=list)
    turn_results: list[AgentTurnResult] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentEvalSummary:
    case_count: int
    passed_count: int
    failed_count: int
    route_accuracy: float
    document_selection_accuracy: float
    clarification_accuracy: float
    unsafe_block_rate: float
    plan_validity_rate: float
    document_scope_safety_rate: float
    tool_policy_compliance_rate: float
    answer_expectation_rate: float


@dataclass(slots=True)
class AgentEvalReport:
    case_results: list[AgentCaseResult] = field(default_factory=list)
    summary: AgentEvalSummary | None = None
    source_path: str | None = None
    filters: dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def case_count(self) -> int:
        return len(self.case_results)

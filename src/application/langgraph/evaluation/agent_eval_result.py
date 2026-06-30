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
    retrieval_strategy_primary: str | None = None
    retrieval_strategy_secondary: list[str] = field(default_factory=list)
    retrieval_strategy_trace_present: bool = False
    retrieval_strategy_fallback_used: bool = False
    retrieval_strategy_enabled: bool = False
    research_plan_present: bool = False
    research_plan_task_count: int = 0
    research_plan_source: str | None = None
    research_task_count: int = 0
    research_task_success_count: int = 0
    research_gap_count: int = 0
    research_report_present: bool = False
    research_report_section_count: int = 0
    research_citation_count: int = 0
    research_trace_present: bool = False
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
    retrieval_strategy_selection_rate: float
    retrieval_strategy_validity_rate: float
    strategy_fallback_rate: float
    multi_strategy_success_rate: float
    strategy_document_scope_safety_rate: float
    strategy_trace_coverage_rate: float
    guardrail_block_rate: float = 0.0
    out_of_scope_redirect_rate: float = 0.0
    false_positive_guardrail_rate: float = 0.0
    false_negative_guardrail_rate: float = 0.0
    prompt_injection_block_rate: float = 0.0
    destructive_tool_block_rate: float = 0.0
    grounding_failure_catch_rate: float = 0.0
    deep_research_route_accuracy: float = 0.0
    research_plan_validity_rate: float = 0.0
    research_task_success_rate: float = 0.0
    research_gap_detection_rate: float = 0.0
    research_document_scope_safety_rate: float = 0.0
    research_report_completeness_rate: float = 0.0
    research_citation_coverage_rate: float = 0.0


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

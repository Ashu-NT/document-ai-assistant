from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class AgentTurnInput:
    user_input: str
    document: str | None = None
    document_id: str | None = None
    allow_answer_generation: bool = False
    llm_planning_enabled: bool = False
    retrieval_strategy_enabled: bool = False
    llm_retrieval_strategy_enabled: bool = False
    requested_retrieval_strategy: str | None = None
    show_retrieval_strategy: bool = False
    show_context: bool = False
    show_plan: bool = False


@dataclass(frozen=True, slots=True)
class AgentExpectedBehavior:
    final_route: str | None = None
    selected_document_contains: str | None = None
    selected_document_id: str | None = None
    should_clarify: bool | None = None
    should_exit: bool | None = None
    required_tools: list[str] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    required_plan_tools: list[str] = field(default_factory=list)
    forbidden_plan_tools: list[str] = field(default_factory=list)
    answer_must_contain: list[str] = field(default_factory=list)
    answer_must_not_contain: list[str] = field(default_factory=list)
    context_document_id: str | None = None
    unsafe_request_blocked: bool | None = None
    success: bool | None = None
    retrieval_strategy_primary: str | None = None
    retrieval_strategy_secondary_contains: list[str] = field(default_factory=list)
    retrieval_strategy_trace_required: bool | None = None


@dataclass(frozen=True, slots=True)
class AgentTestCase:
    case_id: str
    name: str
    description: str | None
    inputs: list[AgentTurnInput]
    expected: AgentExpectedBehavior
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def turn_count(self) -> int:
        return len(self.inputs)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

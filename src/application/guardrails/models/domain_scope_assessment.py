from __future__ import annotations

from dataclasses import dataclass, field

from src.application.guardrails.models.domain_scope_category import DomainScopeCategory


@dataclass(slots=True, frozen=True)
class DomainScopeAssessment:
    category: DomainScopeCategory
    reason: str
    matched_terms: list[str] = field(default_factory=list)
    requires_clarification: bool = False

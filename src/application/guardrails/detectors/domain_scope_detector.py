from __future__ import annotations

import re

from src.application.guardrails.models.domain_scope_assessment import (
    DomainScopeAssessment,
)
from src.application.guardrails.models.domain_scope_category import DomainScopeCategory
from src.application.guardrails.policies.domain_scope_policy import DomainScopePolicy

_AMBIGUOUS_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"^(tell me about (it|this|that)|what does that mean|explain this|can you help( me)?)[\?\.\s]*$",
        re.IGNORECASE,
    ),
    re.compile(r"^(what|how|why|when|where|who)\??$", re.IGNORECASE),
    re.compile(r"^(it|this|that|these|those)[\?\.\s]*$", re.IGNORECASE),
)
_GENERIC_SCOPE_FOLLOW_UP_RE = re.compile(
    r"^(?:what|when|where|how)\s+(?:is|are|was|were|should|do|does)\s+(?:the\s+)?[a-z0-9 _-]+[\?\.\s]*$",
    re.IGNORECASE,
)


class DomainScopeDetector:
    def __init__(self, policy: DomainScopePolicy | None = None) -> None:
        self.policy = policy or DomainScopePolicy()

    def detect(self, user_input: str, *, selected_document_id: str | None = None) -> DomainScopeAssessment:
        normalized = " ".join(user_input.strip().lower().split())
        if not normalized:
            return DomainScopeAssessment(
                category=DomainScopeCategory.UNKNOWN_AMBIGUOUS,
                reason="Input was empty after normalization.",
                requires_clarification=True,
            )

        command_matches = [
            signal for signal in self.policy.command_signals if signal in normalized
        ]
        if command_matches:
            return DomainScopeAssessment(
                category=DomainScopeCategory.DEMO_RUNTIME_COMMAND,
                reason="Matched a supported document-agent runtime command.",
                matched_terms=command_matches,
            )

        out_of_scope_matches = [
            signal for signal in self.policy.out_of_scope_signals if signal in normalized
        ]
        if out_of_scope_matches:
            return DomainScopeAssessment(
                category=DomainScopeCategory.OUT_OF_SCOPE_GENERAL,
                reason="Request is unrelated to indexed technical documents.",
                matched_terms=out_of_scope_matches,
            )

        scope_matches = [
            signal for signal in self.policy.allowed_scope_signals if signal in normalized
        ]
        if scope_matches:
            if self._requires_document_clarification(
                normalized=normalized,
                scope_matches=scope_matches,
                selected_document_id=selected_document_id,
            ):
                return DomainScopeAssessment(
                    category=DomainScopeCategory.UNKNOWN_AMBIGUOUS,
                    reason="Request is in the document domain but still needs a selected or referenced document.",
                    matched_terms=scope_matches,
                    requires_clarification=True,
                )
            return DomainScopeAssessment(
                category=DomainScopeCategory.DOCUMENT_AGENT_SCOPE,
                reason="Request contains document-grounded or technical-document scope signals.",
                matched_terms=scope_matches,
            )

        word_count = len(normalized.split())
        if word_count < self.policy.minimum_meaningful_words or any(
            pattern.match(normalized) for pattern in _AMBIGUOUS_PATTERNS
        ):
            return DomainScopeAssessment(
                category=DomainScopeCategory.UNKNOWN_AMBIGUOUS,
                reason="Request is too ambiguous to route confidently.",
                requires_clarification=not bool(selected_document_id),
            )

        if selected_document_id:
            return DomainScopeAssessment(
                category=DomainScopeCategory.DOCUMENT_AGENT_SCOPE,
                reason="A document is already selected, so the ambiguous request is treated as in-scope follow-up.",
            )

        return DomainScopeAssessment(
            category=DomainScopeCategory.UNKNOWN_AMBIGUOUS,
            reason="Request does not clearly map to a supported document-agent task.",
            requires_clarification=True,
        )

    @staticmethod
    def _requires_document_clarification(
        *,
        normalized: str,
        scope_matches: list[str],
        selected_document_id: str | None,
    ) -> bool:
        if selected_document_id:
            return False
        if len(scope_matches) > 1:
            return False
        if len(normalized.split()) > 4:
            return False
        return _GENERIC_SCOPE_FOLLOW_UP_RE.match(normalized) is not None

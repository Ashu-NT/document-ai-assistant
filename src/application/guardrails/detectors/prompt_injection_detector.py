from __future__ import annotations

from src.application.guardrails.models.detector_match import DetectorMatch
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.policies.prompt_injection_policy import (
    PromptInjectionPolicy,
)


class PromptInjectionDetector:
    def __init__(self, policy: PromptInjectionPolicy | None = None) -> None:
        self.policy = policy or PromptInjectionPolicy()

    def detect(self, user_input: str) -> DetectorMatch:
        normalized = " ".join(user_input.strip().lower().split())
        if not normalized:
            return DetectorMatch(matched=False)
        matched_terms = [
            marker for marker in self.policy.blocked_markers if marker in normalized
        ]
        if not matched_terms:
            return DetectorMatch(matched=False)
        return DetectorMatch(
            matched=True,
            reason="Request attempts prompt injection, hidden-instruction access, or chain-of-thought exposure.",
            matched_terms=matched_terms,
            severity=GuardrailSeverity.HIGH,
        )

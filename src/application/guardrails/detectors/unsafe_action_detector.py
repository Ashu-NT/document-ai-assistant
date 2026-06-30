from __future__ import annotations

from dataclasses import dataclass, field

from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.policies.unsafe_action_policy import UnsafeActionPolicy


@dataclass(frozen=True, slots=True)
class UnsafeActionDecision:
    is_unsafe: bool
    reason: str | None = None
    matched_terms: list[str] = field(default_factory=list)
    severity: GuardrailSeverity = GuardrailSeverity.HIGH


class UnsafeActionDetector:
    def __init__(self, policy: UnsafeActionPolicy | None = None) -> None:
        self.policy = policy or UnsafeActionPolicy()

    def detect(self, user_input: str) -> UnsafeActionDecision:
        normalized = " ".join(user_input.strip().lower().split())
        if not normalized:
            return UnsafeActionDecision(is_unsafe=False)

        direct_matches = [
            phrase
            for phrase in self.policy.direct_blocked_phrases
            if phrase in normalized
        ]
        if direct_matches:
            return UnsafeActionDecision(
                is_unsafe=True,
                reason="Request attempts destructive corpus mutation.",
                matched_terms=direct_matches,
                severity=GuardrailSeverity.CRITICAL,
            )

        matched_terms: list[str] = []
        destructive_verb = _first_present(normalized, self.policy.destructive_verbs)
        mutating_verb = _first_present(normalized, self.policy.mutating_verbs)
        corpus_object = _first_present(normalized, self.policy.corpus_objects)
        mass_modifier = _first_present(normalized, self.policy.mass_modifiers)

        if destructive_verb and corpus_object:
            matched_terms.extend([destructive_verb, corpus_object])
            if mass_modifier:
                matched_terms.append(mass_modifier)
            return UnsafeActionDecision(
                is_unsafe=True,
                reason="Request combines destructive action with corpus storage objects.",
                matched_terms=_dedupe_preserving_order(matched_terms),
                severity=GuardrailSeverity.CRITICAL,
            )

        if mutating_verb and corpus_object:
            matched_terms.extend([mutating_verb, corpus_object])
            if mass_modifier:
                matched_terms.append(mass_modifier)
            return UnsafeActionDecision(
                is_unsafe=True,
                reason="Request attempts whole-corpus reingestion or rebuild.",
                matched_terms=_dedupe_preserving_order(matched_terms),
                severity=GuardrailSeverity.HIGH,
            )

        return UnsafeActionDecision(is_unsafe=False)


def _first_present(value: str, candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in value:
            return candidate
    return None


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered

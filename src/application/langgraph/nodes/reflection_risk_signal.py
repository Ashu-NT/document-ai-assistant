from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_HIGH_STAKES_ANSWER_INTENTS = frozenset(
    {
        "safety_warnings",
        "procedure_steps",
        "troubleshooting",
        "certification_summary",
        "maintenance_summary",
    }
)
_HIGH_STAKES_COVERAGE_REQUIREMENTS = frozenset({"ordered_procedure", "exhaustive_list"})


@dataclass(frozen=True, slots=True)
class ReflectionRiskSignal:

    is_llm_generated: bool
    is_contested_intent: bool
    is_compound_question: bool
    is_evidence_truncated: bool
    is_evidence_conflicting: bool
    is_high_stakes_coverage: bool
    is_high_stakes_intent: bool

    @property
    def requires_reflection(self) -> bool:

        if not self.is_llm_generated:
            return False
        return (
            self.is_contested_intent
            or self.is_compound_question
            or self.is_evidence_truncated
            or self.is_evidence_conflicting
            or self.is_high_stakes_coverage
            or self.is_high_stakes_intent
        )


def compute_reflection_risk_signal(answer_payload: Any) -> ReflectionRiskSignal:
    diagnostics = (
        answer_payload.get("diagnostics") if isinstance(answer_payload, dict) else None
    )
    if not isinstance(diagnostics, dict):
        return ReflectionRiskSignal(
            is_llm_generated=False,
            is_contested_intent=False,
            is_compound_question=False,
            is_evidence_truncated=False,
            is_evidence_conflicting=False,
            is_high_stakes_coverage=False,
            is_high_stakes_intent=False,
        )

    decision_trace = diagnostics.get("decision_trace")
    is_llm_generated = bool(
        decision_trace.get("llm_used") if isinstance(decision_trace, dict) else False
    )
    bypass_reason = diagnostics.get("deterministic_dispatch_bypass_reason")
    appendix_truncation = diagnostics.get("raw_source_appendix_truncation")
    is_evidence_truncated = bool(diagnostics.get("prompt_payload_truncated")) or bool(
        appendix_truncation.get("truncated")
        if isinstance(appendix_truncation, dict)
        else False
    )
    conflicts = diagnostics.get("evidence_conflicts") or []
    is_evidence_conflicting = bool(bypass_reason == "conflicting_evidence") or any(
        isinstance(conflict, dict) and conflict.get("is_critical")
        for conflict in conflicts
    )
    return ReflectionRiskSignal(
        is_llm_generated=is_llm_generated,
        is_contested_intent=bypass_reason == "contested_intent",
        is_compound_question=bypass_reason == "compound_question",
        is_evidence_truncated=is_evidence_truncated,
        is_evidence_conflicting=is_evidence_conflicting,
        is_high_stakes_coverage=(
            diagnostics.get("coverage_requirement") in _HIGH_STAKES_COVERAGE_REQUIREMENTS
        ),
        is_high_stakes_intent=(
            diagnostics.get("answer_intent") in _HIGH_STAKES_ANSWER_INTENTS
        ),
    )

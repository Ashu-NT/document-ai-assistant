from __future__ import annotations

from src.application.langgraph.reflection.detectors.coverage_requirement_context_detector import (
    claims_completeness,
    has_step_sequence_gap,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.validation.reflection_validator_context import (
    ValidatorDowngradeContext,
    accept_with_limitations,
)
from src.application.services.answer_generation.coverage import (
    EXHAUSTIVE_LIST,
    ORDERED_PROCEDURE,
)


def check_exhaustive_list_completeness_claim(
    *,
    decision: ReflectionDecision,
    coverage_requirement: str | None,
    evidence_truncated: bool,
    answer_text: str,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    """PR 9 (answering_flow_weakness_remediation_plan.md, W5): an
    EXHAUSTIVE_LIST answer must never claim completeness while the evidence
    that fed generation was truncated (PR 8's flag) -- the model has no way
    to know it was shown a capped view, so a "here are all the X" claim
    could be confidently wrong about being exhaustive."""
    if decision.decision != ReflectionDecisionType.ACCEPT:
        return None
    if coverage_requirement != EXHAUSTIVE_LIST or not evidence_truncated:
        return None
    if not claims_completeness(answer_text):
        return None
    return accept_with_limitations(
        confidence=normalized_confidence,
        reason=(
            "The answer reads as a complete list, but the underlying "
            "evidence was truncated before generation -- it may not "
            "actually be exhaustive."
        ),
        diagnostics={**ctx.diagnostics, "validator": "exhaustive_list_truncated"},
    )


def check_ordered_procedure_step_gap(
    *,
    decision: ReflectionDecision,
    coverage_requirement: str | None,
    answer_text: str,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    """PR 9: an ORDERED_PROCEDURE answer with a detected gap in its own step
    numbering (e.g. "Step 1 ... Step 3", no Step 2) must flag the gap
    instead of presenting a confident-looking partial procedure -- a
    missing step in a maintenance/installation procedure is a safety-
    relevant omission, not a cosmetic one."""
    if decision.decision != ReflectionDecisionType.ACCEPT:
        return None
    if coverage_requirement != ORDERED_PROCEDURE:
        return None
    if not has_step_sequence_gap(answer_text):
        return None
    return accept_with_limitations(
        confidence=normalized_confidence,
        reason=(
            "The procedure's step numbering has a gap, suggesting a step "
            "may be missing from the available evidence."
        ),
        diagnostics={**ctx.diagnostics, "validator": "ordered_procedure_step_gap"},
    )

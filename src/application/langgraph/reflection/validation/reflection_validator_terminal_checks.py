from __future__ import annotations

from src.application.langgraph.reflection.detectors.spare_parts_list_context_detector import (
    is_legitimate_partial_spare_parts_answer,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.services.query_ambiguity_detector import (
    AmbiguousIntentTie,
)
from src.application.langgraph.reflection.validation.reflection_validator_context import (
    ValidatorDowngradeContext,
    accept_with_limitations,
)


def check_clarify(
    *,
    decision: ReflectionDecision,
    policy: ReflectionPolicy,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
    ambiguous_intent_tie: AmbiguousIntentTie | None,
) -> ReflectionDecision | None:
    if decision.decision != ReflectionDecisionType.CLARIFY:
        return None
    if (
        ctx.maintenance_interval_context or ctx.generic_context_applies
    ) and not ctx.hard_grounding_violation:
        return accept_with_limitations(
            confidence=normalized_confidence,
            reason=(
                f"The question is clear enough to answer from the selected "
                f"document, but the grounded {ctx.downgrade_evidence_description} "
                f"answer may be incomplete."
            ),
            diagnostics={**ctx.diagnostics, "validator": "clarify_downgraded"},
        )
    if not policy.allow_clarification:
        return ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=normalized_confidence,
            reason="Reflection requested clarification, but clarification is disabled by policy.",
            diagnostics={**ctx.diagnostics, "validator": "clarification_disabled"},
        )
    if not decision.clarification_question:
        # A CLARIFY decision only exists to give the user a chance to
        # disambiguate. If there is no actual clarification question to
        # ask, silently serving whatever answer/evidence happens to exist
        # would defeat the point and could serve a wrong answer with no
        # chance to clarify -- fail safe instead, regardless of whether
        # evidence happens to exist.
        #
        # Exception: a genuine, generic ambiguity signal (an exact scoring
        # tie between two RetrievalQueryIntent candidates -- works for any
        # pair of intents, no domain keyword list needed) lets us synthesize
        # a real clarification question instead of failing outright.
        if ambiguous_intent_tie is not None:
            return ReflectionDecision(
                decision=ReflectionDecisionType.CLARIFY,
                confidence=normalized_confidence,
                reason=(
                    "The question could refer to more than one topic in this document."
                ),
                clarification_question=(
                    f"Are you asking about {ambiguous_intent_tie.intent_label} "
                    f"or {ambiguous_intent_tie.runner_up_label}?"
                ),
                missing_information=[
                    ambiguous_intent_tie.intent_label,
                    ambiguous_intent_tie.runner_up_label,
                ],
                diagnostics={**ctx.diagnostics, "validator": "ambiguous_intent_clarify"},
            )
        return ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=normalized_confidence,
            reason="Reflection requested clarification without a clarification question.",
            diagnostics={**ctx.diagnostics, "validator": "missing_clarification_question"},
        )
    return None


def check_fail(
    *,
    decision: ReflectionDecision,
    answer_text: str,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    if decision.decision != ReflectionDecisionType.FAIL:
        return None
    if (
        ctx.maintenance_interval_context or ctx.generic_context_applies
    ) and not ctx.hard_grounding_violation:
        return accept_with_limitations(
            confidence=normalized_confidence,
            reason=(
                f"Reflection marked the answer as failed, but grounded "
                f"{ctx.downgrade_evidence_description} exists in the selected document."
            ),
            diagnostics={**ctx.diagnostics, "validator": "fail_downgraded"},
        )
    if (
        ctx.spare_parts_list_context
        and is_legitimate_partial_spare_parts_answer(answer_text)
        and not ctx.hard_grounding_violation
    ):
        return accept_with_limitations(
            confidence=normalized_confidence,
            reason=(
                "Reflection marked the answer as failed, but it is "
                "grounded in the retrieved spare parts table evidence "
                "and already lists real sections, pages, or parsed rows."
            ),
            diagnostics={
                **ctx.diagnostics,
                "validator": "spare_parts_list_fail_downgraded",
            },
        )
    return None


def check_reflection_attempts_limit(
    *,
    reflection_attempts: int,
    policy: ReflectionPolicy,
    answer_text: str,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    if reflection_attempts <= policy.max_reflection_attempts:
        return None
    if (
        ctx.maintenance_interval_context or ctx.generic_context_applies
    ) and not ctx.hard_grounding_violation:
        return accept_with_limitations(
            confidence=normalized_confidence,
            reason=(
                f"Reflection attempt limit was exceeded, but grounded "
                f"{ctx.downgrade_evidence_description} is already available."
            ),
            diagnostics={**ctx.diagnostics, "validator": "reflection_limit_downgraded"},
        )
    if (
        ctx.spare_parts_list_context
        and is_legitimate_partial_spare_parts_answer(answer_text)
        and not ctx.hard_grounding_violation
    ):
        return accept_with_limitations(
            confidence=normalized_confidence,
            reason=(
                "Reflection attempt limit was exceeded, but the answer is "
                "grounded in the retrieved spare parts table evidence and "
                "already lists real sections, pages, or parsed rows."
            ),
            diagnostics={
                **ctx.diagnostics,
                "validator": "spare_parts_list_reflection_limit_downgraded",
            },
        )
    return ReflectionDecision(
        decision=ReflectionDecisionType.FAIL,
        confidence=normalized_confidence,
        reason="Reflection attempt limit has been exceeded.",
        diagnostics={**ctx.diagnostics, "validator": "reflection_limit"},
    )

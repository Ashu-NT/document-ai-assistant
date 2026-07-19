from __future__ import annotations

from src.application.langgraph.reflection.detectors.spare_parts_list_context_detector import (
    is_legitimate_partial_spare_parts_answer,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.validation.reflection_validator_context import (
    ValidatorDowngradeContext,
    accept_with_limitations,
)


def check_duplicate_answer_content(
    *,
    decision: ReflectionDecision,
    has_duplicate_answer_content: bool,
    question: str,
    policy: ReflectionPolicy,
    retrieval_retry_count: int,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    if not (
        has_duplicate_answer_content
        and decision.decision
        in {
            ReflectionDecisionType.ACCEPT,
            ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
        }
    ):
        return None
    if policy.allow_retrieval_retry and retrieval_retry_count < policy.max_retrieval_retries:
        return ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=normalized_confidence,
            reason=(
                "The answer repeated duplicated content instead of a clean grounded summary."
            ),
            retry_query=question,
            missing_information=["deduplicated grounded answer"],
            diagnostics={
                **ctx.diagnostics,
                "validator": "duplicate_answer_content_retry",
                "hard_grounding_violation": "duplicate_answer_content",
            },
        )
    return ReflectionDecision(
        decision=ReflectionDecisionType.FAIL,
        confidence=normalized_confidence,
        reason=(
            "The answer repeated duplicated content instead of a clean grounded summary."
        ),
        diagnostics={
            **ctx.diagnostics,
            "validator": "duplicate_answer_content_fail",
            "hard_grounding_violation": "duplicate_answer_content",
        },
    )


def check_retrieve_again(
    *,
    decision: ReflectionDecision,
    answer_text: str,
    policy: ReflectionPolicy,
    retrieval_retry_count: int,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    if decision.decision != ReflectionDecisionType.RETRIEVE_AGAIN:
        return None
    if (
        ctx.spare_parts_list_context
        and is_legitimate_partial_spare_parts_answer(answer_text)
        and not ctx.hard_grounding_violation
    ):
        return accept_with_limitations(
            confidence=normalized_confidence,
            reason=(
                "The answer is grounded in the retrieved spare parts "
                "table evidence and already lists real sections, "
                "pages, or parsed rows; retrying would not add value."
            ),
            diagnostics={
                **ctx.diagnostics,
                "validator": "spare_parts_list_incomplete_downgraded",
            },
        )
    if not policy.allow_retrieval_retry:
        if (
            ctx.maintenance_interval_context or ctx.generic_context_applies
        ) and not ctx.hard_grounding_violation:
            return accept_with_limitations(
                confidence=normalized_confidence,
                reason=(
                    f"Reflection requested another retrieval attempt, but grounded "
                    f"{ctx.downgrade_evidence_description} already exists in the selected document."
                ),
                diagnostics={**ctx.diagnostics, "validator": "retry_disabled_downgraded"},
            )
        return ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=normalized_confidence,
            reason="Reflection requested retry, but retry is disabled by policy.",
            diagnostics={**ctx.diagnostics, "validator": "retry_disabled"},
        )
    if retrieval_retry_count >= policy.max_retrieval_retries:
        if (
            ctx.maintenance_interval_context or ctx.generic_context_applies
        ) and not ctx.hard_grounding_violation:
            return accept_with_limitations(
                confidence=normalized_confidence,
                reason=(
                    f"Reflection retry limit was reached, but grounded "
                    f"{ctx.downgrade_evidence_description} is already available."
                ),
                diagnostics={**ctx.diagnostics, "validator": "retry_limit_downgraded"},
            )
        return ReflectionDecision(
            decision=ReflectionDecisionType.FAIL,
            confidence=normalized_confidence,
            reason="Reflection retry limit has already been reached.",
            diagnostics={**ctx.diagnostics, "validator": "retry_limit"},
        )
    return None

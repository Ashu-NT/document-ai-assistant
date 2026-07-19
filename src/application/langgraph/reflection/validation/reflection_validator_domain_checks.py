from __future__ import annotations

from src.application.langgraph.reflection.detectors.identifier_inventory_context_detector import (
    answer_contains_identifier_inventory,
)
from src.application.langgraph.reflection.detectors.spare_parts_list_context_detector import (
    answer_denies_spare_parts_list,
    answer_only_has_unit_artifact_rows,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.validation.reflection_validator_context import (
    ValidatorDowngradeContext,
)


def check_identifier_inventory(
    *,
    decision: ReflectionDecision,
    answer_text: str,
    policy: ReflectionPolicy,
    retrieval_retry_count: int,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    if not (
        ctx.identifier_inventory_context
        and decision.decision
        in {
            ReflectionDecisionType.ACCEPT,
            ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
            ReflectionDecisionType.CLARIFY,
        }
        and not answer_contains_identifier_inventory(answer_text)
    ):
        return None
    if policy.allow_retrieval_retry and retrieval_retry_count < policy.max_retrieval_retries:
        return ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=normalized_confidence,
            reason=(
                "The answer did not actually list the requested identifiers "
                "even though grounded evidence exists in the selected document."
            ),
            retry_query="serial number part number identifier list",
            missing_information=["explicit identifier values"],
            diagnostics={
                **ctx.diagnostics,
                "validator": "identifier_inventory_retry",
            },
        )
    return ReflectionDecision(
        decision=ReflectionDecisionType.FAIL,
        confidence=normalized_confidence,
        reason=(
            "The answer did not actually list the requested identifiers "
            "from the grounded document evidence."
        ),
        diagnostics={
            **ctx.diagnostics,
            "validator": "identifier_inventory_missing_values",
        },
    )


def check_spare_parts_list(
    *,
    decision: ReflectionDecision,
    answer_text: str,
    policy: ReflectionPolicy,
    retrieval_retry_count: int,
    normalized_confidence: float,
    ctx: ValidatorDowngradeContext,
) -> ReflectionDecision | None:
    if not (
        ctx.spare_parts_list_context
        and decision.decision
        in {
            ReflectionDecisionType.ACCEPT,
            ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
        }
    ):
        return None
    denies_list = answer_denies_spare_parts_list(answer_text)
    artifact_only = answer_only_has_unit_artifact_rows(answer_text)
    if not (denies_list or artifact_only):
        return None
    if denies_list:
        retry_reason = (
            "The answer denied that a spare parts list or table "
            "exists, but grounded spare parts table evidence was "
            "already retrieved in the selected document."
        )
        fail_reason = (
            "The answer denied that a spare parts list or table "
            "exists even though grounded spare parts table evidence "
            "was retrieved in the selected document."
        )
    else:
        retry_reason = (
            "The answer only contained header or unit artifacts "
            "(such as a bare quantity/unit value) instead of real "
            "spare parts rows, even though grounded spare parts "
            "table evidence was already retrieved."
        )
        fail_reason = (
            "The answer only contained header or unit artifacts "
            "instead of real spare parts rows from the grounded "
            "spare parts table evidence."
        )
    if policy.allow_retrieval_retry and retrieval_retry_count < policy.max_retrieval_retries:
        return ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=normalized_confidence,
            reason=retry_reason,
            retry_query="spare parts list table position quantity denomination part number",
            missing_information=["spare parts table rows"],
            diagnostics={
                **ctx.diagnostics,
                "validator": (
                    "spare_parts_list_denial_retry"
                    if denies_list
                    else "spare_parts_list_artifact_only_retry"
                ),
            },
        )
    return ReflectionDecision(
        decision=ReflectionDecisionType.FAIL,
        confidence=normalized_confidence,
        reason=fail_reason,
        diagnostics={
            **ctx.diagnostics,
            "validator": (
                "spare_parts_list_denial_missing_values"
                if denies_list
                else "spare_parts_list_artifact_only_missing_values"
            ),
        },
    )

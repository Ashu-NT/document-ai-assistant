from __future__ import annotations

from src.application.langgraph.reflection.detectors.identifier_inventory_context_detector import (
    answer_contains_identifier_inventory,
    is_selected_document_identifier_inventory_context,
)
from src.application.langgraph.reflection.detectors.maintenance_interval_context_detector import (
    is_selected_document_maintenance_interval_context,
)
from src.application.langgraph.reflection.detectors.spare_parts_list_context_detector import (
    answer_denies_spare_parts_list,
    answer_only_has_unit_artifact_rows,
    is_legitimate_partial_spare_parts_answer,
    is_selected_document_spare_parts_list_context,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy


class ReflectionValidator:
    def validate(
        self,
        *,
        decision: ReflectionDecision,
        policy: ReflectionPolicy,
        reflection_attempts: int,
        retrieval_retry_count: int,
        selected_document_id: str | None,
        context_document_ids: list[str],
        question: str = "",
        answer_intent: str | None = None,
        answer_text: str = "",
        has_useful_evidence: bool = False,
        has_relevant_maintenance_evidence: bool = False,
        has_relevant_spare_parts_evidence: bool = False,
    ) -> ReflectionDecision:
        diagnostics = dict(decision.diagnostics)
        normalized_confidence = min(max(float(decision.confidence), 0.0), 1.0)
        decision.confidence = normalized_confidence
        maintenance_interval_context = is_selected_document_maintenance_interval_context(
            question=question,
            answer_intent=answer_intent,
            selected_document_id=selected_document_id,
            has_relevant_maintenance_evidence=has_relevant_maintenance_evidence,
        )
        identifier_inventory_context = is_selected_document_identifier_inventory_context(
            question=question,
            answer_intent=answer_intent,
            selected_document_id=selected_document_id,
            has_useful_evidence=has_useful_evidence,
        )
        spare_parts_list_context = is_selected_document_spare_parts_list_context(
            question=question,
            has_relevant_spare_parts_evidence=has_relevant_spare_parts_evidence,
        )
        has_answer_or_evidence = bool(answer_text.strip()) or has_useful_evidence

        if (
            policy.require_document_scope
            and selected_document_id is not None
            and any(document_id != selected_document_id for document_id in context_document_ids)
        ):
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=1.0,
                reason="Reflection detected document-scope leakage in the evidence set.",
                diagnostics={**diagnostics, "validator": "scope_violation"},
            )

        if decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN:
            if spare_parts_list_context and is_legitimate_partial_spare_parts_answer(
                answer_text
            ):
                return _accept_with_limitations(
                    confidence=normalized_confidence,
                    reason=(
                        "The answer is grounded in the retrieved spare parts "
                        "table evidence and already lists real sections, "
                        "pages, or parsed rows; retrying would not add value."
                    ),
                    diagnostics={
                        **diagnostics,
                        "validator": "spare_parts_list_incomplete_downgraded",
                    },
                )
            if not policy.allow_retrieval_retry:
                if maintenance_interval_context:
                    return _accept_with_limitations(
                        confidence=normalized_confidence,
                        reason=(
                            "Reflection requested another retrieval attempt, but grounded "
                            "maintenance interval evidence already exists in the selected document."
                        ),
                        diagnostics={**diagnostics, "validator": "retry_disabled_downgraded"},
                )
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection requested retry, but retry is disabled by policy.",
                    diagnostics={**diagnostics, "validator": "retry_disabled"},
                )
            if retrieval_retry_count >= policy.max_retrieval_retries:
                if maintenance_interval_context:
                    return _accept_with_limitations(
                        confidence=normalized_confidence,
                        reason=(
                            "Reflection retry limit was reached, but grounded maintenance "
                            "interval evidence is already available."
                        ),
                        diagnostics={**diagnostics, "validator": "retry_limit_downgraded"},
                    )
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection retry limit has already been reached.",
                    diagnostics={**diagnostics, "validator": "retry_limit"},
                )

        if (
            identifier_inventory_context
            and decision.decision
            in {
                ReflectionDecisionType.ACCEPT,
                ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
                ReflectionDecisionType.CLARIFY,
            }
            and not answer_contains_identifier_inventory(answer_text)
        ):
            if (
                policy.allow_retrieval_retry
                and retrieval_retry_count < policy.max_retrieval_retries
            ):
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
                        **diagnostics,
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
                    **diagnostics,
                    "validator": "identifier_inventory_missing_values",
                },
            )

        if spare_parts_list_context and decision.decision in {
            ReflectionDecisionType.ACCEPT,
            ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
        }:
            denies_list = answer_denies_spare_parts_list(answer_text)
            artifact_only = answer_only_has_unit_artifact_rows(answer_text)
            if denies_list or artifact_only:
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
                if (
                    policy.allow_retrieval_retry
                    and retrieval_retry_count < policy.max_retrieval_retries
                ):
                    return ReflectionDecision(
                        decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                        confidence=normalized_confidence,
                        reason=retry_reason,
                        retry_query=(
                            "spare parts list table position quantity "
                            "denomination part number"
                        ),
                        missing_information=["spare parts table rows"],
                        diagnostics={
                            **diagnostics,
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
                        **diagnostics,
                        "validator": (
                            "spare_parts_list_denial_missing_values"
                            if denies_list
                            else "spare_parts_list_artifact_only_missing_values"
                        ),
                    },
                )

        if decision.decision == ReflectionDecisionType.CLARIFY:
            if maintenance_interval_context:
                return _accept_with_limitations(
                    confidence=normalized_confidence,
                    reason=(
                        "The question is clear enough to answer from the selected "
                        "document, but the grounded maintenance interval answer may be incomplete."
                    ),
                    diagnostics={**diagnostics, "validator": "clarify_downgraded"},
                )
            if not policy.allow_clarification:
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection requested clarification, but clarification is disabled by policy.",
                    diagnostics={**diagnostics, "validator": "clarification_disabled"},
                )
            if not decision.clarification_question:
                if has_answer_or_evidence:
                    return _accept_with_limitations(
                        confidence=normalized_confidence,
                        reason=(
                            "Reflection requested clarification without a clarification "
                            "question, but useful grounded evidence already exists."
                        ),
                        diagnostics={
                            **diagnostics,
                            "validator": "missing_clarification_question_downgraded",
                        },
                    )
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection requested clarification without a clarification question.",
                    diagnostics={**diagnostics, "validator": "missing_clarification_question"},
                )

        if decision.decision == ReflectionDecisionType.FAIL:
            if maintenance_interval_context:
                return _accept_with_limitations(
                    confidence=normalized_confidence,
                    reason=(
                        "Reflection marked the answer as failed, but grounded maintenance "
                        "interval evidence exists in the selected document."
                    ),
                    diagnostics={**diagnostics, "validator": "fail_downgraded"},
                )
            if spare_parts_list_context and is_legitimate_partial_spare_parts_answer(
                answer_text
            ):
                return _accept_with_limitations(
                    confidence=normalized_confidence,
                    reason=(
                        "Reflection marked the answer as failed, but it is "
                        "grounded in the retrieved spare parts table evidence "
                        "and already lists real sections, pages, or parsed rows."
                    ),
                    diagnostics={
                        **diagnostics,
                        "validator": "spare_parts_list_fail_downgraded",
                    },
                )

        if reflection_attempts > policy.max_reflection_attempts:
            if maintenance_interval_context:
                return _accept_with_limitations(
                    confidence=normalized_confidence,
                    reason=(
                        "Reflection attempt limit was exceeded, but grounded maintenance "
                        "interval evidence is already available."
                    ),
                    diagnostics={**diagnostics, "validator": "reflection_limit_downgraded"},
                )
            if spare_parts_list_context and is_legitimate_partial_spare_parts_answer(
                answer_text
            ):
                return _accept_with_limitations(
                    confidence=normalized_confidence,
                    reason=(
                        "Reflection attempt limit was exceeded, but the answer is "
                        "grounded in the retrieved spare parts table evidence and "
                        "already lists real sections, pages, or parsed rows."
                    ),
                    diagnostics={
                        **diagnostics,
                        "validator": "spare_parts_list_reflection_limit_downgraded",
                    },
                )
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=normalized_confidence,
                reason="Reflection attempt limit has been exceeded.",
                diagnostics={**diagnostics, "validator": "reflection_limit"},
            )

        return decision


def _accept_with_limitations(
    *,
    confidence: float,
    reason: str,
    diagnostics: dict[str, object],
) -> ReflectionDecision:
    return ReflectionDecision(
        decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
        confidence=confidence,
        reason=reason,
        diagnostics=diagnostics,
    )

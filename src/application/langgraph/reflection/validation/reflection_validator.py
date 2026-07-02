from __future__ import annotations

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
    ) -> ReflectionDecision:
        diagnostics = dict(decision.diagnostics)
        normalized_confidence = min(max(float(decision.confidence), 0.0), 1.0)
        decision.confidence = normalized_confidence
        maintenance_interval_context = _is_selected_document_maintenance_interval_context(
            question=question,
            answer_intent=answer_intent,
            selected_document_id=selected_document_id,
            has_relevant_maintenance_evidence=has_relevant_maintenance_evidence,
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

        if (
            decision.decision == ReflectionDecisionType.FAIL
            and maintenance_interval_context
        ):
            return _accept_with_limitations(
                confidence=normalized_confidence,
                reason=(
                    "Reflection marked the answer as failed, but grounded maintenance "
                    "interval evidence exists in the selected document."
                ),
                diagnostics={**diagnostics, "validator": "fail_downgraded"},
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


def _is_selected_document_maintenance_interval_context(
    *,
    question: str,
    answer_intent: str | None,
    selected_document_id: str | None,
    has_relevant_maintenance_evidence: bool,
) -> bool:
    if not selected_document_id or not has_relevant_maintenance_evidence:
        return False
    normalized_question = question.lower()
    normalized_intent = (answer_intent or "").lower()
    if "maintenance_summary" not in normalized_intent and "maintenance" not in normalized_question:
        return False
    return any(
        marker in normalized_question
        for marker in (
            "maintenance interval",
            "maintenance intervals",
            "service interval",
            "service intervals",
            "inspection interval",
            "inspection intervals",
            "maintenance schedule",
            "preventive maintenance",
            "how often",
            "schedule",
        )
    )

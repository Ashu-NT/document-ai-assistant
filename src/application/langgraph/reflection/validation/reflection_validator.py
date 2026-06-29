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
    ) -> ReflectionDecision:
        diagnostics = dict(decision.diagnostics)
        normalized_confidence = min(max(float(decision.confidence), 0.0), 1.0)
        decision.confidence = normalized_confidence

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
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection requested retry, but retry is disabled by policy.",
                    diagnostics={**diagnostics, "validator": "retry_disabled"},
                )
            if retrieval_retry_count >= policy.max_retrieval_retries:
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection retry limit has already been reached.",
                    diagnostics={**diagnostics, "validator": "retry_limit"},
                )

        if decision.decision == ReflectionDecisionType.CLARIFY:
            if not policy.allow_clarification:
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection requested clarification, but clarification is disabled by policy.",
                    diagnostics={**diagnostics, "validator": "clarification_disabled"},
                )
            if not decision.clarification_question:
                return ReflectionDecision(
                    decision=ReflectionDecisionType.FAIL,
                    confidence=normalized_confidence,
                    reason="Reflection requested clarification without a clarification question.",
                    diagnostics={**diagnostics, "validator": "missing_clarification_question"},
                )

        if reflection_attempts > policy.max_reflection_attempts:
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=normalized_confidence,
                reason="Reflection attempt limit has been exceeded.",
                diagnostics={**diagnostics, "validator": "reflection_limit"},
            )

        return decision

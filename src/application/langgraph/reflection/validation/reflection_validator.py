from __future__ import annotations

from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
    SufficiencyVerdict,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.services.query_ambiguity_detector import (
    AmbiguousIntentTie,
)
from src.application.langgraph.reflection.validation.reflection_validator_context import (
    build_downgrade_context,
)
from src.application.langgraph.reflection.validation.reflection_validator_domain_checks import (
    check_identifier_inventory,
    check_spare_parts_list,
)
from src.application.langgraph.reflection.validation.reflection_validator_retry_checks import (
    check_duplicate_answer_content,
    check_retrieve_again,
)
from src.application.langgraph.reflection.validation.reflection_validator_terminal_checks import (
    check_clarify,
    check_fail,
    check_reflection_attempts_limit,
)


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
        has_unexpected_page_references: bool = False,
        has_duplicate_answer_content: bool = False,
        generic_sufficiency_verdict: SufficiencyVerdict | None = None,
        ambiguous_intent_tie: AmbiguousIntentTie | None = None,
    ) -> ReflectionDecision:
        normalized_confidence = min(max(float(decision.confidence), 0.0), 1.0)
        decision.confidence = normalized_confidence
        ctx = build_downgrade_context(
            decision=decision,
            question=question,
            answer_intent=answer_intent,
            selected_document_id=selected_document_id,
            has_useful_evidence=has_useful_evidence,
            has_relevant_maintenance_evidence=has_relevant_maintenance_evidence,
            has_relevant_spare_parts_evidence=has_relevant_spare_parts_evidence,
            generic_sufficiency_verdict=generic_sufficiency_verdict,
        )

        if (
            policy.require_document_scope
            and selected_document_id is not None
            and any(document_id != selected_document_id for document_id in context_document_ids)
        ):
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=1.0,
                reason="Reflection detected document-scope leakage in the evidence set.",
                diagnostics={**ctx.diagnostics, "validator": "scope_violation"},
            )
        if has_unexpected_page_references:
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=normalized_confidence,
                reason=(
                    "The answer cited pages outside the approved evidence for this turn."
                ),
                diagnostics={
                    **ctx.diagnostics,
                    "validator": "unexpected_answer_pages",
                    "hard_grounding_violation": "unexpected_answer_pages",
                },
            )

        checks = (
            lambda: check_duplicate_answer_content(
                decision=decision,
                has_duplicate_answer_content=has_duplicate_answer_content,
                question=question,
                policy=policy,
                retrieval_retry_count=retrieval_retry_count,
                normalized_confidence=normalized_confidence,
                ctx=ctx,
            ),
            lambda: check_retrieve_again(
                decision=decision,
                answer_text=answer_text,
                policy=policy,
                retrieval_retry_count=retrieval_retry_count,
                normalized_confidence=normalized_confidence,
                ctx=ctx,
            ),
            lambda: check_identifier_inventory(
                decision=decision,
                answer_text=answer_text,
                policy=policy,
                retrieval_retry_count=retrieval_retry_count,
                normalized_confidence=normalized_confidence,
                ctx=ctx,
            ),
            lambda: check_spare_parts_list(
                decision=decision,
                answer_text=answer_text,
                policy=policy,
                retrieval_retry_count=retrieval_retry_count,
                normalized_confidence=normalized_confidence,
                ctx=ctx,
            ),
            lambda: check_clarify(
                decision=decision,
                policy=policy,
                normalized_confidence=normalized_confidence,
                ctx=ctx,
                ambiguous_intent_tie=ambiguous_intent_tie,
            ),
            lambda: check_fail(
                decision=decision,
                answer_text=answer_text,
                normalized_confidence=normalized_confidence,
                ctx=ctx,
            ),
            lambda: check_reflection_attempts_limit(
                reflection_attempts=reflection_attempts,
                policy=policy,
                answer_text=answer_text,
                normalized_confidence=normalized_confidence,
                ctx=ctx,
            ),
        )
        for check in checks:
            result = check()
            if result is not None:
                return result

        return decision

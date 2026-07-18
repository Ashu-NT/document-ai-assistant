from __future__ import annotations

from typing import Any

from src.application.langgraph.reflection.evaluators.maintenance_evidence_relevance_detector import (
    MaintenanceEvidenceRelevanceDetector,
)
from src.application.langgraph.reflection.models import (
    AnswerQuality,
    EvidenceQuality,
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy


class DeterministicReflectionDecider:
    @staticmethod
    def decide(
        *,
        policy: ReflectionPolicy,
        answer_quality: AnswerQuality,
        evidence_quality: EvidenceQuality,
        question: str,
        answer: str,
        answer_intent: str | None,
        citations: list[dict[str, Any]],
        selected_document_id: str | None,
        approved_chunks: list[dict[str, Any]],
        retrieval_retry_count: int,
    ) -> ReflectionDecision:
        lower_question = question.lower()
        lower_intent = (answer_intent or "").lower()
        normalized_answer = answer.lower()
        has_relevant_maintenance_evidence = (
            MaintenanceEvidenceRelevanceDetector.has_relevant_evidence(
                question=question,
                answer_intent=answer_intent,
                approved_chunks=approved_chunks,
                selected_document_id=selected_document_id,
            )
        )
        maintenance_interval_question = (
            MaintenanceEvidenceRelevanceDetector.is_maintenance_interval_question(
                question=lower_question,
                answer_intent=lower_intent,
            )
        )
        if evidence_quality.has_document_leakage:
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=1.0,
                reason="Evidence leaked outside the selected document scope.",
            )
        if answer_quality.unexpected_pages:
            decision = (
                ReflectionDecisionType.FAIL
                if retrieval_retry_count >= policy.max_retrieval_retries
                else ReflectionDecisionType.RETRIEVE_AGAIN
            )
            return ReflectionDecision(
                decision=decision,
                confidence=0.96,
                reason=(
                    "The answer cited pages outside the approved evidence for this turn."
                ),
                retry_query=question if decision == ReflectionDecisionType.RETRIEVE_AGAIN else None,
                missing_information=["page-aligned grounded answer"],
                diagnostics={"hard_grounding_violation": "unexpected_answer_pages"},
            )
        if answer_quality.has_duplicate_content:
            decision = (
                ReflectionDecisionType.FAIL
                if retrieval_retry_count >= policy.max_retrieval_retries
                else ReflectionDecisionType.RETRIEVE_AGAIN
            )
            return ReflectionDecision(
                decision=decision,
                confidence=0.9,
                reason=(
                    "The answer repeated materially duplicated content instead of a clean grounded summary."
                ),
                retry_query=question if decision == ReflectionDecisionType.RETRIEVE_AGAIN else None,
                missing_information=["deduplicated grounded answer"],
                diagnostics={"hard_grounding_violation": "duplicate_answer_content"},
            )
        if maintenance_interval_question and not has_relevant_maintenance_evidence:
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=0.95,
                reason=(
                    "No relevant maintenance interval evidence was found in the "
                    "selected document."
                ),
                missing_information=["maintenance interval evidence"],
            )
        if not evidence_quality.has_sufficient_evidence:
            return ReflectionDecision(
                decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                confidence=0.9,
                reason="The answer did not have enough approved evidence.",
                # No real reformulation signal exists here -- pin retry_query
                # to the original question itself (rather than leaving it
                # unset) so the retry reformulation strategy uses it verbatim
                # instead of falling back to appending "additional grounded evidence"
                # boilerplate that adds no real search signal and can dilute
                # keyword/BM25 relevance. The existing top_k increase on
                # retry is what actually broadens recall here.
                retry_query=question,
                missing_information=["additional grounded evidence"],
            )
        if maintenance_interval_question:
            if MaintenanceEvidenceRelevanceDetector.contains_unrelated_specifications(
                normalized_answer
            ):
                if (
                    has_relevant_maintenance_evidence
                    and retrieval_retry_count >= policy.max_retrieval_retries
                ):
                    return ReflectionDecision(
                        decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
                        confidence=0.72,
                        reason=(
                            "Relevant maintenance interval evidence exists, but the "
                            "current answer still mixes in unrelated specifications."
                        ),
                        missing_information=["clean maintenance-only answer"],
                    )
                return ReflectionDecision(
                    decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                    confidence=0.9,
                    reason=(
                        "The answer mixed maintenance intervals with unrelated "
                        "technical specifications."
                    ),
                    retry_query=(
                        "maintenance intervals preventive maintenance schedule "
                        "operating hours only"
                    ),
                    missing_information=["maintenance interval evidence only"],
                )
            if not answer_quality.contains_page_reference or not citations:
                if has_relevant_maintenance_evidence:
                    return ReflectionDecision(
                        decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
                        confidence=0.76,
                        reason=(
                            "Relevant maintenance interval evidence exists, but the "
                            "answer may be incomplete because grounded references are weak."
                        ),
                        missing_information=["explicit page references"],
                    )
                return ReflectionDecision(
                    decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                    confidence=0.85,
                    reason="The maintenance interval answer must include grounded references.",
                    retry_query=(
                        "maintenance intervals preventive maintenance schedule "
                        "with page references"
                    ),
                    missing_information=["maintenance interval references"],
                )
            if not MaintenanceEvidenceRelevanceDetector.has_interval_structure(
                normalized_answer
            ):
                if has_relevant_maintenance_evidence:
                    return ReflectionDecision(
                        decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
                        confidence=0.74,
                        reason=(
                            "Relevant maintenance interval evidence exists, but the "
                            "answer may be incomplete because interval structure is weak."
                        ),
                        missing_information=["clear interval or frequency structure"],
                    )
                return ReflectionDecision(
                    decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                    confidence=0.82,
                    reason=(
                        "The maintenance interval answer did not clearly organize "
                        "interval or frequency information."
                    ),
                    retry_query=(
                        "maintenance intervals daily weekly monthly annual "
                        "operating hours"
                    ),
                    missing_information=["interval or frequency structure"],
                )
            if not answer_quality.complete_enough:
                return ReflectionDecision(
                    decision=ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
                    confidence=0.78,
                    reason=(
                        "The answer is grounded in maintenance interval evidence, "
                        "but it may not cover every interval completely."
                    ),
                    missing_information=["possibly missing interval details"],
                )
        if (
            "maintenance" in lower_question
            and "maintenance" in lower_intent
            and "interval" not in lower_question
            and answer_quality.score < policy.minimum_answer_quality_score
        ):
            return ReflectionDecision(
                decision=ReflectionDecisionType.CLARIFY,
                confidence=0.7,
                reason="The question may require clarification between tasks, intervals, and procedures.",
                clarification_question=(
                    "Do you want maintenance tasks, maintenance intervals, or maintenance procedures?"
                ),
                missing_information=[
                    "maintenance tasks",
                    "maintenance intervals",
                    "maintenance procedures",
                ],
            )
        if (
            answer_quality.score >= policy.minimum_answer_quality_score
            and evidence_quality.score >= policy.minimum_evidence_quality_score
        ):
            return ReflectionDecision(
                decision=ReflectionDecisionType.ACCEPT,
                confidence=0.85,
                reason="The answer is grounded and supported by approved evidence.",
            )
        return ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.75,
            reason="The answer appears incomplete for the current evidence set.",
            # Same rationale as the insufficient-evidence branch above: no
            # real reformulation signal exists for this generic case, so keep
            # the retry query identical to the original question instead of
            # diluting it with non-search-term boilerplate.
            retry_query=question,
            missing_information=["more specific supporting evidence"],
        )

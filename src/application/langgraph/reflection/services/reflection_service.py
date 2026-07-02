from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.application.langgraph.reflection.models import (
    AnswerQuality,
    EvidenceQuality,
    ReflectionDecision,
    ReflectionDecisionType,
    ReflectionResult,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.prompts import (
    REFLECTION_PROMPT_VERSION,
    ReflectionPromptBuilder,
)
from src.application.langgraph.reflection.services.reflection_json_parser import (
    ReflectionJsonParser,
)
from src.application.langgraph.reflection.validation import ReflectionValidator
from src.application.services.ai import LLMService
from src.shared.exceptions import ApplicationError


class ReflectionService:
    def __init__(
        self,
        *,
        llm_service: LLMService | None = None,
        prompt_builder: ReflectionPromptBuilder | None = None,
        json_parser: ReflectionJsonParser | None = None,
        validator: ReflectionValidator | None = None,
        policy: ReflectionPolicy | None = None,
        model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or ReflectionPromptBuilder()
        self.json_parser = json_parser or ReflectionJsonParser()
        self.validator = validator or ReflectionValidator()
        self.policy = policy or ReflectionPolicy()
        self.model = model

    def review(
        self,
        *,
        original_user_question: str,
        generated_answer: str,
        selected_document_id: str | None,
        selected_document_title: str | None,
        answer_intent: str | None,
        approved_chunks: list[dict[str, Any]],
        rejected_chunks: list[dict[str, Any]],
        citations: list[dict[str, Any]],
        reflection_attempts: int,
        retrieval_retry_count: int,
    ) -> ReflectionResult:
        answer_quality = self._score_answer(
            question=original_user_question,
            answer=generated_answer,
            citations=citations,
        )
        evidence_quality = self._score_evidence(
            approved_chunks=approved_chunks,
            rejected_chunks=rejected_chunks,
            selected_document_id=selected_document_id,
        )
        context_document_ids = sorted(
            {
                str(chunk.get("document_id"))
                for chunk in approved_chunks
                if chunk.get("document_id")
            }
        )
        deterministic = self._deterministic_decision(
            answer_quality=answer_quality,
            evidence_quality=evidence_quality,
            question=original_user_question,
            answer=generated_answer,
            answer_intent=answer_intent,
            citations=citations,
        )
        used_llm = False
        raw_llm_decision: ReflectionDecision | None = None
        if self.policy.enabled and self.llm_service is not None and generated_answer.strip():
            try:
                prompt = self.prompt_builder.build(
                    original_user_question=original_user_question,
                    selected_document_id=selected_document_id,
                    selected_document_title=selected_document_title,
                    answer_intent=answer_intent,
                    generated_answer=generated_answer,
                    approved_chunk_summaries=approved_chunks,
                    rejected_chunk_summaries=rejected_chunks,
                    citations=citations,
                    context_document_ids=context_document_ids,
                    reflection_attempt_count=reflection_attempts,
                    retry_count=retrieval_retry_count,
                )
                payload = self.llm_service.generate(prompt, model=self.model)
                raw_llm_decision = self.json_parser.parse(payload)
                used_llm = True
            except ApplicationError:
                raw_llm_decision = None
            except Exception:
                raw_llm_decision = None
        effective_decision = raw_llm_decision or deterministic
        effective_decision = self.validator.validate(
            decision=effective_decision,
            policy=self.policy,
            reflection_attempts=reflection_attempts,
            retrieval_retry_count=retrieval_retry_count,
            selected_document_id=selected_document_id,
            context_document_ids=context_document_ids,
        )
        grounding_score = min(
            answer_quality.score,
            evidence_quality.score,
        )
        document_scope_score = 0.0 if evidence_quality.has_document_leakage else 1.0
        overall_score = round(
            (
                answer_quality.score
                + evidence_quality.score
                + grounding_score
                + document_scope_score
            )
            / 4.0,
            4,
        )
        return ReflectionResult(
            decision=effective_decision,
            answer_quality_score=answer_quality.score,
            evidence_quality_score=evidence_quality.score,
            grounding_score=grounding_score,
            document_scope_score=document_scope_score,
            overall_score=overall_score,
            accepted=effective_decision.decision == ReflectionDecisionType.ACCEPT,
            requires_retry=effective_decision.decision
            == ReflectionDecisionType.RETRIEVE_AGAIN,
            requires_clarification=effective_decision.decision
            == ReflectionDecisionType.CLARIFY,
            failed=effective_decision.decision == ReflectionDecisionType.FAIL,
            diagnostics={
                "used_llm": used_llm,
                "prompt_version": REFLECTION_PROMPT_VERSION,
                "answer_quality": asdict(answer_quality),
                "evidence_quality": asdict(evidence_quality),
                "validator_decision": effective_decision.decision.value,
            },
        )

    @staticmethod
    def _score_answer(
        *,
        question: str,
        answer: str,
        citations: list[dict[str, Any]],
    ) -> AnswerQuality:
        normalized_answer = (answer or "").strip()
        answered_question = bool(normalized_answer)
        contains_page_reference = "page" in normalized_answer.lower() or bool(citations)
        contains_grounding = bool(citations)
        concise_enough = len(normalized_answer) <= 2400 if normalized_answer else False
        question_terms = {
            token
            for token in question.lower().split()
            if len(token) > 3
        }
        answer_terms = set(normalized_answer.lower().split())
        contains_requested_information = bool(question_terms.intersection(answer_terms))
        complete_enough = answered_question and contains_requested_information
        score = round(
            (
                (1.0 if answered_question else 0.0)
                + (1.0 if contains_requested_information else 0.0)
                + (1.0 if contains_page_reference else 0.0)
                + (1.0 if contains_grounding else 0.0)
                + (1.0 if concise_enough else 0.0)
                + (1.0 if complete_enough else 0.0)
            )
            / 6.0,
            4,
        )
        issues: list[str] = []
        if not answered_question:
            issues.append("empty_answer")
        if not contains_requested_information:
            issues.append("weak_question_alignment")
        if not contains_grounding:
            issues.append("missing_grounding")
        return AnswerQuality(
            answered_question=answered_question,
            contains_requested_information=contains_requested_information,
            contains_page_reference=contains_page_reference,
            contains_grounding=contains_grounding,
            complete_enough=complete_enough,
            concise_enough=concise_enough,
            score=score,
            issues=issues,
        )

    @staticmethod
    def _score_evidence(
        *,
        approved_chunks: list[dict[str, Any]],
        rejected_chunks: list[dict[str, Any]],
        selected_document_id: str | None,
    ) -> EvidenceQuality:
        page_numbers: list[int] = []
        document_ids: list[str] = []
        has_document_leakage = False
        for chunk in approved_chunks:
            document_id = chunk.get("document_id")
            if document_id:
                text_id = str(document_id)
                if text_id not in document_ids:
                    document_ids.append(text_id)
                if selected_document_id is not None and text_id != selected_document_id:
                    has_document_leakage = True
            source = chunk.get("source") or {}
            if isinstance(source, dict):
                page_start = source.get("page_start")
                if isinstance(page_start, int):
                    page_numbers.append(page_start)
        has_sufficient_evidence = len(approved_chunks) > 0
        score = round(
            (
                (1.0 if has_sufficient_evidence else 0.0)
                + (0.0 if has_document_leakage else 1.0)
                + (1.0 if page_numbers else 0.0)
            )
            / 3.0,
            4,
        )
        issues: list[str] = []
        if not has_sufficient_evidence:
            issues.append("no_approved_chunks")
        if has_document_leakage:
            issues.append("document_scope_leakage")
        return EvidenceQuality(
            approved_chunk_count=len(approved_chunks),
            rejected_chunk_count=len(rejected_chunks),
            document_ids=document_ids,
            page_numbers=sorted(set(page_numbers)),
            has_document_leakage=has_document_leakage,
            has_sufficient_evidence=has_sufficient_evidence,
            score=score,
            issues=issues,
        )

    def _deterministic_decision(
        self,
        *,
        answer_quality: AnswerQuality,
        evidence_quality: EvidenceQuality,
        question: str,
        answer: str,
        answer_intent: str | None,
        citations: list[dict[str, Any]],
    ) -> ReflectionDecision:
        lower_question = question.lower()
        lower_intent = (answer_intent or "").lower()
        normalized_answer = answer.lower()
        if evidence_quality.has_document_leakage:
            return ReflectionDecision(
                decision=ReflectionDecisionType.FAIL,
                confidence=1.0,
                reason="Evidence leaked outside the selected document scope.",
            )
        if not evidence_quality.has_sufficient_evidence:
            return ReflectionDecision(
                decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                confidence=0.9,
                reason="The answer did not have enough approved evidence.",
                missing_information=["additional grounded evidence"],
            )
        if self._is_maintenance_interval_question(
            question=lower_question,
            answer_intent=lower_intent,
        ):
            if self._contains_unrelated_specifications(normalized_answer):
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
            if not self._has_interval_structure(normalized_answer):
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
        if (
            "maintenance" in lower_question
            and "maintenance" in lower_intent
            and "interval" not in lower_question
            and answer_quality.score < self.policy.minimum_answer_quality_score
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
            answer_quality.score >= self.policy.minimum_answer_quality_score
            and evidence_quality.score >= self.policy.minimum_evidence_quality_score
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
            missing_information=["more specific supporting evidence"],
        )

    @staticmethod
    def _is_maintenance_interval_question(
        *,
        question: str,
        answer_intent: str,
    ) -> bool:
        if "maintenance_summary" not in answer_intent and "maintenance" not in question:
            return False
        return any(
            marker in question
            for marker in (
                "maintenance interval",
                "maintenance intervals",
                "service interval",
                "inspection interval",
                "maintenance schedule",
                "how often",
                "daily",
                "weekly",
                "monthly",
                "annual",
            )
        )

    @staticmethod
    def _contains_unrelated_specifications(answer: str) -> bool:
        return any(
            marker in answer
            for marker in (
                "voltage",
                "installed power",
                "pump type",
                "serial number",
                "tank capacity",
                "nominal speed",
                "rpm",
            )
        )

    @staticmethod
    def _has_interval_structure(answer: str) -> bool:
        return any(
            marker in answer
            for marker in (
                "interval",
                "frequency",
                "operating hours",
                "daily",
                "weekly",
                "monthly",
                "quarterly",
                "annual",
                "annually",
                "every ",
            )
        )

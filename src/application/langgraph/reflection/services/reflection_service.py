from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.application.langgraph.reflection.evaluators.answer_quality_scorer import (
    AnswerQualityScorer,
)
from src.application.langgraph.reflection.evaluators.evidence_quality_scorer import (
    EvidenceQualityScorer,
)
from src.application.langgraph.reflection.evaluators.maintenance_evidence_relevance_detector import (
    MaintenanceEvidenceRelevanceDetector,
)
from src.application.langgraph.reflection.evaluators.spare_parts_evidence_relevance_detector import (
    SparePartsEvidenceRelevanceDetector,
)
from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
    ReflectionResult,
)
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.services.deterministic_reflection_decider import (
    DeterministicReflectionDecider,
)
from src.application.langgraph.reflection.services.reflection_json_parser import (
    ReflectionJsonParser,
)
from src.application.langgraph.reflection.services.reflection_response_schema import (
    build_reflection_response_json_schema,
)
from src.application.langgraph.reflection.validation import ReflectionValidator
from src.application.prompts.reflection import (
    REFLECTION_PROMPT_VERSION,
    ReflectionPromptBuilder,
)
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
        has_relevant_maintenance_evidence = (
            MaintenanceEvidenceRelevanceDetector.has_relevant_evidence(
                question=original_user_question,
                answer_intent=answer_intent,
                approved_chunks=approved_chunks,
                selected_document_id=selected_document_id,
            )
        )
        has_relevant_spare_parts_evidence = (
            SparePartsEvidenceRelevanceDetector.has_relevant_evidence(
                approved_chunks=approved_chunks,
                selected_document_id=selected_document_id,
            )
        )
        answer_quality = AnswerQualityScorer.score(
            question=original_user_question,
            answer=generated_answer,
            citations=citations,
        )
        evidence_quality = EvidenceQualityScorer.score(
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
        deterministic = DeterministicReflectionDecider.decide(
            policy=self.policy,
            answer_quality=answer_quality,
            evidence_quality=evidence_quality,
            question=original_user_question,
            answer=generated_answer,
            answer_intent=answer_intent,
            citations=citations,
            selected_document_id=selected_document_id,
            approved_chunks=approved_chunks,
            retrieval_retry_count=retrieval_retry_count,
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
                payload = self.llm_service.generate(
                    prompt,
                    model=self.model,
                    response_schema=build_reflection_response_json_schema(),
                )
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
            question=original_user_question,
            answer_intent=answer_intent,
            answer_text=generated_answer,
            has_useful_evidence=evidence_quality.has_sufficient_evidence,
            has_relevant_maintenance_evidence=has_relevant_maintenance_evidence,
            has_relevant_spare_parts_evidence=has_relevant_spare_parts_evidence,
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
            accepted=effective_decision.decision
            in {
                ReflectionDecisionType.ACCEPT,
                ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS,
            },
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

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

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
from src.application.langgraph.reflection.decomposition import (
    MultiClauseCoverageScorer,
    QuestionClauseSplitter,
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
from src.application.langgraph.reflection.services.query_ambiguity_detector import (
    QueryAmbiguityDetector,
)
from src.application.langgraph.reflection.services.reflection_response_schema import (
    build_reflection_response_json_schema,
)
from src.application.langgraph.reflection.strategies.evidence_sufficiency import (
    EvidenceSufficiencyContext,
    EvidenceSufficiencyStrategyRegistry,
)
from src.application.langgraph.reflection.validation import ReflectionValidator
from src.application.prompts.reflection import (
    REFLECTION_PROMPT_VERSION,
    ReflectionPromptBuilder,
)
from src.application.services.ai import LLMService
from src.config.logging import get_logger
from src.shared.exceptions import ApplicationError

if TYPE_CHECKING:
    # Deferred: see query_ambiguity_detector.py -- a module-level import
    # here re-enters src.application.langgraph.nodes's __init__ chain,
    # which imports back into this reflection package.
    from src.application.langgraph.nodes.retrieval_intent_decision import (
        RetrievalIntentDecision,
    )

_logger = get_logger(__name__)


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
        evidence_sufficiency_registry: EvidenceSufficiencyStrategyRegistry | None = None,
        query_ambiguity_detector: QueryAmbiguityDetector | None = None,
        question_clause_splitter: QuestionClauseSplitter | None = None,
        multi_clause_coverage_scorer: MultiClauseCoverageScorer | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or ReflectionPromptBuilder()
        self.json_parser = json_parser or ReflectionJsonParser()
        self.validator = validator or ReflectionValidator()
        self.policy = policy or ReflectionPolicy()
        self.model = model
        self.evidence_sufficiency_registry = (
            evidence_sufficiency_registry or EvidenceSufficiencyStrategyRegistry()
        )
        self.query_ambiguity_detector = (
            query_ambiguity_detector or QueryAmbiguityDetector()
        )
        self.question_clause_splitter = question_clause_splitter or QuestionClauseSplitter()
        self.multi_clause_coverage_scorer = (
            multi_clause_coverage_scorer or MultiClauseCoverageScorer()
        )

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
        reference_notes: list[Any] | None = None,
        retrieval_query_intent: str | None = None,
        retrieval_intent_decision: RetrievalIntentDecision | None = None,
        coverage_requirement: str | None = None,
        evidence_truncated: bool = False,
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
        evidence_quality = EvidenceQualityScorer.score(
            approved_chunks=approved_chunks,
            rejected_chunks=rejected_chunks,
            selected_document_id=selected_document_id,
            reference_notes=reference_notes,
            referenced_pages=None,
        )
        answer_quality = AnswerQualityScorer.score(
            question=original_user_question,
            answer=generated_answer,
            citations=citations,
            reference_notes=reference_notes,
            approved_pages=evidence_quality.page_numbers,
        )
        evidence_quality = EvidenceQualityScorer.score(
            approved_chunks=approved_chunks,
            rejected_chunks=rejected_chunks,
            selected_document_id=selected_document_id,
            reference_notes=reference_notes,
            referenced_pages=answer_quality.referenced_pages,
        )
        context_document_ids = sorted(
            {
                str(chunk.get("document_id"))
                for chunk in approved_chunks
                if chunk.get("document_id")
            }
        )
        question_clauses = self.question_clause_splitter.split(original_user_question)
        clause_coverage = (
            self.multi_clause_coverage_scorer.score(
                clauses=question_clauses, answer_text=generated_answer
            )
            if question_clauses.has_multiple_clauses
            else None
        )
        generic_sufficiency_verdict = self.evidence_sufficiency_registry.evaluate(
            retrieval_query_intent=retrieval_query_intent,
            context=EvidenceSufficiencyContext(
                question=original_user_question,
                answer_text=generated_answer,
                answer_intent=answer_intent,
                selected_document_id=selected_document_id,
                approved_chunks=approved_chunks,
                rejected_chunks=rejected_chunks,
                evidence_quality=evidence_quality,
                answer_quality=answer_quality,
                clause_coverage=clause_coverage,
            ),
        )
        ambiguous_intent_tie = self.query_ambiguity_detector.detect(
            original_user_question,
            retrieval_intent_decision=retrieval_intent_decision,
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
            clause_coverage=clause_coverage,
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
            has_unexpected_page_references=bool(answer_quality.unexpected_pages),
            has_duplicate_answer_content=answer_quality.has_duplicate_content,
            generic_sufficiency_verdict=generic_sufficiency_verdict,
            ambiguous_intent_tie=ambiguous_intent_tie,
            coverage_requirement=coverage_requirement,
            evidence_truncated=evidence_truncated,
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
        _logger.info(
            "reflection_score_recorded",
            extra={
                "decision": effective_decision.decision.value,
                "answer_quality_score": answer_quality.score,
                "evidence_quality_score": evidence_quality.score,
                "grounding_score": grounding_score,
                "overall_score": overall_score,
                "intent": answer_intent,
            },
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
                "retrieval_query_intent": retrieval_query_intent,
                "coverage_requirement": coverage_requirement,
                "evidence_truncated": evidence_truncated,
                "evidence_sufficiency_verdict": generic_sufficiency_verdict.verdict.value,
                "ambiguous_intent_tie": (
                    {
                        "intent_label": ambiguous_intent_tie.intent_label,
                        "runner_up_label": ambiguous_intent_tie.runner_up_label,
                    }
                    if ambiguous_intent_tie is not None
                    else None
                ),
                "clause_coverage": (
                    {
                        "uncovered_clauses": list(clause_coverage.uncovered_clauses),
                        "is_fully_covered": clause_coverage.is_fully_covered,
                    }
                    if clause_coverage is not None
                    else None
                ),
            },
        )

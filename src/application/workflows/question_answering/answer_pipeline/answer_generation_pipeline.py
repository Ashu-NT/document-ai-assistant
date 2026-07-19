from typing import Callable

from src.application.contracts.guardrails import GuardrailResult
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.guardrails.context.context_guardrail_chain import ContextGuardrailChain
from src.application.guardrails.services import PreGenerationGuardrailService
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.application.workflows.question_answering.answer_pipeline.decision_trace_builder import (
    build_decision_trace,
)
from src.application.workflows.question_answering.answer_pipeline.post_answer_disposition_resolver import (
    PostAnswerDispositionResolver,
)
from src.application.workflows.question_answering.answer_pipeline.post_answer_guardrail_evaluator import (
    PostAnswerGuardrailEvaluator,
)
from src.application.workflows.question_answering.answer_pipeline.structured_evidence_merger import (
    StructuredEvidenceMerger,
)
from src.application.workflows.question_answering.answer_pipeline.structured_fact_joiner import (
    StructuredFactJoiner,
)
from src.application.workflows.question_answering.question_answering_request import (
    QuestionAnsweringRequest,
)
from src.application.workflows.question_answering.question_answering_result import (
    QuestionAnsweringResult,
)
from src.application.workflows.question_answering.question_answering_route import (
    QuestionAnsweringRoute,
)
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.application.workflows.shared.document_scope_filter import (
    partition_chunks_by_document_scope,
)
from src.domain.retrieval import RetrievalQuery
from src.shared.progress.progress_emitter import emit_progress

_ANSWER_GENERATION_DISABLED_MESSAGE = (
    "I found relevant document evidence, but answer generation is not enabled yet."
)
_ANSWER_GENERATION_NOT_CONFIGURED_MESSAGE = (
    "Answer generation is not configured."
)


class AnswerGenerationPipeline:
    """Runs the retrieved/approved chunks through context guardrails,
    document-scope enforcement, structured-evidence resolution, answer
    generation, and post-answer guardrails -- the main orchestration for
    turning a set of evidence chunks into a `QuestionAnsweringResult`."""

    def __init__(
        self,
        *,
        context_guardrail_chain: ContextGuardrailChain,
        pre_generation_guardrail_service: PreGenerationGuardrailService,
        answer_generation_service: AnswerGenerationService | None,
        post_answer_guardrails: list,
        structured_evidence_merger: StructuredEvidenceMerger,
        structured_fact_joiner: StructuredFactJoiner,
    ) -> None:
        self._context_guardrail_chain = context_guardrail_chain
        self._pre_generation_guardrail_service = pre_generation_guardrail_service
        self._answer_generation_service = answer_generation_service
        self._post_answer_guardrails = post_answer_guardrails
        self._post_answer_guardrail_evaluator = PostAnswerGuardrailEvaluator(
            post_answer_guardrails
        )
        self._post_answer_disposition_resolver = PostAnswerDispositionResolver(
            evaluator=self._post_answer_guardrail_evaluator,
            answer_generation_service=answer_generation_service,
        )
        self._structured_evidence_merger = structured_evidence_merger
        self._structured_fact_joiner = structured_fact_joiner

    def run(
        self,
        *,
        request: QuestionAnsweringRequest,
        analyzed_query: RetrievalQuery,
        analyzed_intent: str,
        allow_generation: bool,
        workflow_result: RetrievalWorkflowResult,
        progress_callback: Callable[[str], None] | None = None,
    ) -> QuestionAnsweringResult:

        # Phase 4: context guardrails — filter, budget, quality
        emit_progress(progress_callback, "Checking context guardrails...")
        approved_chunks, context_blocking = self._context_guardrail_chain.run(
            retrieved_chunks=workflow_result.final_chunks,
            query_text=request.question,
            document_id=request.document_id,
        )
        if context_blocking is not None:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL,
                safe_user_message=context_blocking.safe_user_message,
                guardrail_decision=context_blocking.decision,
                guardrail_result=context_blocking,
                retrieval_result=workflow_result,
                diagnostics={"blocked_by": "context_guardrail"},
            )

        scope_violation = self._document_scope_violation(
            approved_chunks=approved_chunks,
            document_id=request.document_id,
        )
        if scope_violation is not None:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL,
                safe_user_message=scope_violation.safe_user_message,
                guardrail_decision=scope_violation.decision,
                guardrail_result=scope_violation,
                retrieval_result=workflow_result,
                diagnostics={
                    "blocked_by": "document_scope_guardrail",
                    **workflow_result.diagnostics,
                },
            )

        all_chunk_ids = {c.chunk_id for c in workflow_result.final_chunks}
        approved_ids = [c.chunk_id for c in approved_chunks]
        approved_id_set = set(approved_ids)
        rejected_chunk_ids = [
            cid for cid in all_chunk_ids if cid not in approved_id_set
        ]

        best_score = workflow_result.retrieval_result.best_score()
        confidence = str(round(best_score, 4)) if best_score is not None else None
        structured_evidence = self._structured_evidence_merger.merge(
            request=request,
            analyzed_query=analyzed_query,
            workflow_result=workflow_result,
        )
        resolved_identifiers = list(structured_evidence.identifiers)
        resolved_structured_entities = list(structured_evidence.structured_entities)

        # Phase 5: answer generation
        if not allow_generation:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.RETRIEVAL_QA,
                answer_text=_ANSWER_GENERATION_DISABLED_MESSAGE,
                retrieval_result=workflow_result,
                approved_chunk_ids=approved_ids,
                rejected_chunk_ids=rejected_chunk_ids,
                resolved_identifiers=resolved_identifiers,
                resolved_structured_entities=resolved_structured_entities,
                confidence=confidence,
                diagnostics={
                    "enough_evidence": workflow_result.enough_evidence,
                    **workflow_result.diagnostics,
                },
            )

        if self._answer_generation_service is None:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.RETRIEVAL_QA,
                answer_text=_ANSWER_GENERATION_NOT_CONFIGURED_MESSAGE,
                retrieval_result=workflow_result,
                approved_chunk_ids=approved_ids,
                rejected_chunk_ids=rejected_chunk_ids,
                resolved_identifiers=resolved_identifiers,
                resolved_structured_entities=resolved_structured_entities,
                confidence=confidence,
                diagnostics={
                    "enough_evidence": workflow_result.enough_evidence,
                    **workflow_result.diagnostics,
                },
            )

        pre_generation_result = self._pre_generation_guardrail_service.check(
            GuardrailContext(
                user_input=request.question,
                query_text=request.question,
                route=QuestionAnsweringRoute.RETRIEVAL_QA.value,
                document_id=request.document_id,
                selected_document_id=request.document_id,
                query_intent=analyzed_intent,
                query_chunk_types=[chunk_type.value for chunk_type in analyzed_query.chunk_types],
                approved_chunks=list(approved_chunks),
                evidence_chunks=list(approved_chunks),
                runtime_mode="workflow",
            )
        )
        if not pre_generation_result.allowed:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL,
                safe_user_message=pre_generation_result.safe_user_message,
                guardrail_decision=pre_generation_result.decision,
                guardrail_result=pre_generation_result,
                retrieval_result=workflow_result,
                approved_chunk_ids=approved_ids,
                rejected_chunk_ids=rejected_chunk_ids,
                resolved_identifiers=resolved_identifiers,
                resolved_structured_entities=resolved_structured_entities,
                diagnostics={"blocked_by": "pre_generation_guardrail"},
            )

        # LLM only ever sees approved_chunks (plus any structured-fact source
        # chunks joined in below)
        emit_progress(progress_callback, "Generating answer...")
        join_result = self._structured_fact_joiner.join(
            approved_chunks=approved_chunks,
            analyzed_query=analyzed_query,
            question=request.question,
            resolved_identifiers=resolved_identifiers,
            resolved_structured_entities=resolved_structured_entities,
        )
        joined_chunks = join_result.chunks
        structured_context = join_result.structured_context
        intent_decision = join_result.intent_decision
        resolved_identifiers = join_result.resolved_identifiers
        resolved_structured_entities = join_result.resolved_structured_entities
        # Recomputed from the chunks actually sent to generation, not the
        # pre-join/pre-prepare `approved_chunks` above: `join()` can both add
        # chunks (a resolved identifier/entity's source chunk that normal
        # retrieval missed) and remove them (FinalEvidencePreparer's own
        # dedup/pruning) -- reporting the earlier, stale set as "approved"
        # would misrepresent what a caller sees reflected in the answer.
        approved_ids = [chunk.chunk_id for chunk in joined_chunks]
        approved_id_set = set(approved_ids)
        rejected_chunk_ids = [
            cid for cid in all_chunk_ids if cid not in approved_id_set
        ]
        gen_request = AnswerGenerationRequest(
            question=request.question,
            context_chunks=joined_chunks,
            show_raw_evidence=request.show_raw_evidence,
            query_intent=analyzed_intent,
            retrieval_intent=analyzed_intent,
            chunk_type_preferences=list(analyzed_query.chunk_types),
            route=QuestionAnsweringRoute.RETRIEVAL_QA.value,
            resolved_identifiers=resolved_identifiers,
            resolved_structured_entities=resolved_structured_entities,
            structured_context=structured_context,
            answer_intent_decision=intent_decision,
        )
        generated = self._answer_generation_service.generate(gen_request)

        # Phase 6: post-answer guardrails (PR 11,
        # answering_flow_weakness_remediation_plan.md, closes W8) -- every
        # disposition above WARN used to be a no-op; this now regenerates
        # once on REGENERATE, and never loops a second time. The regenerate
        # loop and terminal-result construction live in
        # PostAnswerDispositionResolver, not here, to keep this method's
        # own length manageable.
        emit_progress(progress_callback, "Checking answer guardrails...")
        chunk_type_values = [
            chunk_type.value for chunk_type in analyzed_query.chunk_types
        ]
        evaluation = self._post_answer_guardrail_evaluator.evaluate(
            generated=generated,
            question=request.question,
            analyzed_intent=analyzed_intent,
            chunk_types=chunk_type_values,
            approved_chunks=approved_chunks,
        )
        disposition_outcome = self._post_answer_disposition_resolver.resolve(
            generated=generated,
            evaluation=evaluation,
            gen_request=gen_request,
            question=request.question,
            analyzed_intent=analyzed_intent,
            chunk_types=chunk_type_values,
            approved_chunks=approved_chunks,
            common_result_kwargs={
                "retrieval_result": workflow_result,
                "approved_chunk_ids": approved_ids,
                "rejected_chunk_ids": rejected_chunk_ids,
                "resolved_identifiers": resolved_identifiers,
                "resolved_structured_entities": resolved_structured_entities,
            },
        )
        if disposition_outcome.terminal_result is not None:
            return disposition_outcome.terminal_result
        generated = disposition_outcome.generated
        evaluation = disposition_outcome.evaluation
        regenerated_once = disposition_outcome.regenerated_once

        emit_progress(progress_callback, "Answer ready.")
        return QuestionAnsweringResult(
            route=QuestionAnsweringRoute.RETRIEVAL_QA,
            answer_text=generated.answer_text,
            citations=generated.citations,
            retrieval_result=workflow_result,
            approved_chunk_ids=approved_ids,
            rejected_chunk_ids=rejected_chunk_ids,
            resolved_identifiers=resolved_identifiers,
            resolved_structured_entities=resolved_structured_entities,
            confidence=confidence,
            answer_intent=generated.answer_intent,
            limitation_note=generated.limitation_note,
            sections=generated.sections,
            reference_notes=generated.reference_notes,
            diagnostics={
                "enough_evidence": workflow_result.enough_evidence,
                "prompt_version": generated.prompt_version,
                "model_name": generated.model_name,
                "retry_query": request.retry_query,
                **generated.diagnostics,
                **workflow_result.diagnostics,
                **(
                    {"post_answer_guardrail_warnings": evaluation.warnings}
                    if evaluation.warnings
                    else {}
                ),
                **(
                    {"post_answer_regenerated": True} if regenerated_once else {}
                ),
                "decision_trace": build_decision_trace(
                    analyzed_query=analyzed_query,
                    generated=generated,
                ),
            },
        )

    @staticmethod
    def _document_scope_violation(
        *,
        approved_chunks: list,
        document_id: str | None,
    ) -> GuardrailResult | None:
        if document_id is None:
            return None

        _, leaking_chunks = partition_chunks_by_document_scope(
            approved_chunks, document_id
        )
        if not leaking_chunks:
            return None

        return GuardrailResult(
            decision=GuardrailDecision.INSUFFICIENT_EVIDENCE,
            allowed=False,
            reason="Approved chunks leaked outside the selected document scope.",
            safe_user_message=(
                "The selected document scope could not be enforced safely for this answer."
            ),
        )

from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.guardrails.guardrail_runner import GuardrailRunner
from src.application.guardrails.context.context_guardrail_chain import ContextGuardrailChain
from src.application.guardrails.services import PreGenerationGuardrailService
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.application.services.document_exploration.document_exploration_service import (
    DocumentExplorationService,
    DocumentNotFoundError,
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
from src.application.workflows.question_answering.question_answering_router import (
    QuestionAnsweringRouter,
)
from src.application.workflows.retrieval.retrieval_workflow import RetrievalWorkflow
from src.application.workflows.retrieval.retrieval_workflow_result import (
    RetrievalWorkflowResult,
)
from src.domain.common import new_id
from src.domain.retrieval import RetrievalQuery
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieval_result import RetrievalResult
from src.application.contracts.guardrails import GuardrailResult

_ANSWER_GENERATION_DISABLED_MESSAGE = (
    "I found relevant document evidence, but answer generation is not enabled yet."
)
_ANSWER_GENERATION_NOT_CONFIGURED_MESSAGE = (
    "Answer generation is not configured."
)


def _default_allow_answer_generation() -> bool:
    try:
        from src.config.settings import ingestion_settings

        return ingestion_settings.enable_answer_generation
    except Exception:
        return False


class QuestionAnsweringWorkflow:
    def __init__(
        self,
        retrieval_workflow: RetrievalWorkflow,
        exploration_service: DocumentExplorationService,
        router: QuestionAnsweringRouter | None = None,
        pre_query_guardrails: list[Guardrail] | None = None,
        context_guardrails: list[Guardrail] | None = None,
        pre_generation_guardrail_service: PreGenerationGuardrailService | None = None,
        answer_generation_service: AnswerGenerationService | None = None,
        post_answer_guardrails: list[Guardrail] | None = None,
    ) -> None:
        self._retrieval_workflow = retrieval_workflow
        self._exploration_service = exploration_service
        self._router = router or QuestionAnsweringRouter()
        self._pre_query_guardrails: list[Guardrail] = pre_query_guardrails or []
        self._context_guardrail_chain = ContextGuardrailChain(context_guardrails or [])
        self._pre_generation_guardrail_service = (
            pre_generation_guardrail_service or PreGenerationGuardrailService()
        )
        self._answer_generation_service = answer_generation_service
        self._post_answer_guardrails: list[Guardrail] = post_answer_guardrails or []

    def run(self, request: QuestionAnsweringRequest) -> QuestionAnsweringResult:
        allow_generation = request.allow_answer_generation

        if self._pre_query_guardrails:
            context = GuardrailContext(
                user_input=request.question,
                query_text=request.question,
                document_id=request.document_id,
                selected_document_id=request.document_id,
            )
            blocking = GuardrailRunner(self._pre_query_guardrails).run(context)
            if blocking is not None:
                route = (
                    QuestionAnsweringRoute.NEEDS_CLARIFICATION
                    if blocking.decision == GuardrailDecision.NEEDS_CLARIFICATION
                    else QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL
                )
                return QuestionAnsweringResult(
                    route=route,
                    safe_user_message=blocking.safe_user_message,
                    guardrail_decision=blocking.decision,
                    guardrail_result=blocking,
                )

        route, analyzed_query, analyzed_intent = self._router.decide(
            question=request.question,
            top_k=request.top_k or 5,
            document_id=request.document_id,
        )

        if route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION:
            return self._handle_exploration(request)

        if request.context_override_chunks is not None:
            workflow_result = self._build_override_workflow_result(
                request=request,
                analyzed_query=analyzed_query,
            )
            return self._answer_from_chunks(
                request=request,
                analyzed_query=analyzed_query,
                analyzed_intent=analyzed_intent,
                allow_generation=allow_generation,
                workflow_result=workflow_result,
            )

        return self._handle_retrieval(
            request,
            analyzed_query,
            analyzed_intent.value,
            allow_generation,
        )

    def _handle_exploration(
        self, request: QuestionAnsweringRequest
    ) -> QuestionAnsweringResult:
        if not request.document_id:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.DOCUMENT_EXPLORATION,
                safe_user_message="Please specify a document to explore.",
                diagnostics={"reason": "missing_document_id"},
            )

        try:
            exploration_result = self._exploration_service.explore(request.document_id)
        except DocumentNotFoundError:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.DOCUMENT_EXPLORATION,
                safe_user_message="The requested document was not found.",
                diagnostics={"document_id": request.document_id},
            )

        return QuestionAnsweringResult(
            route=QuestionAnsweringRoute.DOCUMENT_EXPLORATION,
            document_exploration_result=exploration_result,
            diagnostics={"document_id": request.document_id},
        )

    def _handle_retrieval(
        self,
        request: QuestionAnsweringRequest,
        analyzed_query: RetrievalQuery,
        analyzed_intent: str,
        allow_generation: bool = False,
    ) -> QuestionAnsweringResult:
        workflow_result = self._retrieval_workflow.run(analyzed_query)
        return self._answer_from_chunks(
            request=request,
            analyzed_query=analyzed_query,
            analyzed_intent=analyzed_intent,
            allow_generation=allow_generation,
            workflow_result=workflow_result,
        )

    def _answer_from_chunks(
        self,
        *,
        request: QuestionAnsweringRequest,
        analyzed_query: RetrievalQuery,
        analyzed_intent: str,
        allow_generation: bool,
        workflow_result: RetrievalWorkflowResult,
    ) -> QuestionAnsweringResult:

        # Phase 4: context guardrails — filter, budget, quality
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
        rejected_chunk_ids = [
            cid for cid in all_chunk_ids if cid not in set(approved_ids)
        ]

        best_score = workflow_result.retrieval_result.best_score()
        confidence = str(round(best_score, 4)) if best_score is not None else None

        # Phase 5: answer generation
        if not allow_generation:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.RETRIEVAL_QA,
                answer_text=_ANSWER_GENERATION_DISABLED_MESSAGE,
                retrieval_result=workflow_result,
                approved_chunk_ids=approved_ids,
                rejected_chunk_ids=rejected_chunk_ids,
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
                diagnostics={"blocked_by": "pre_generation_guardrail"},
            )

        # LLM only ever sees approved_chunks
        gen_request = AnswerGenerationRequest(
            question=request.question,
            context_chunks=approved_chunks,
            query_intent=analyzed_intent,
            retrieval_intent=analyzed_intent,
            chunk_type_preferences=list(analyzed_query.chunk_types),
            document_id=request.document_id,
            require_citations=request.require_citations,
            route=QuestionAnsweringRoute.RETRIEVAL_QA.value,
            resolved_identifiers=list(request.resolved_identifiers),
        )
        generated = self._answer_generation_service.generate(gen_request)

        # Phase 6: post-answer guardrails
        if self._post_answer_guardrails:
            post_context = GuardrailContext(
                query_text=request.question,
                query_intent=analyzed_intent,
                query_chunk_types=[chunk_type.value for chunk_type in analyzed_query.chunk_types],
                approved_chunks=approved_chunks,
                answer_text=generated.answer_text,
                answer_intent=(
                    generated.answer_intent.value
                    if generated.answer_intent is not None
                    else None
                ),
                metadata=generated.diagnostics,
            )
            post_blocking = GuardrailRunner(self._post_answer_guardrails).run(
                post_context
            )
            if post_blocking is not None:
                return QuestionAnsweringResult(
                    route=QuestionAnsweringRoute.BLOCKED_BY_GUARDRAIL,
                    safe_user_message=post_blocking.safe_user_message,
                    guardrail_decision=post_blocking.decision,
                    guardrail_result=post_blocking,
                    retrieval_result=workflow_result,
                    approved_chunk_ids=approved_ids,
                    rejected_chunk_ids=rejected_chunk_ids,
                    diagnostics={"blocked_by": "post_answer_guardrail"},
                )

        return QuestionAnsweringResult(
            route=QuestionAnsweringRoute.RETRIEVAL_QA,
            answer_text=generated.answer_text,
            citations=generated.citations,
            retrieval_result=workflow_result,
            approved_chunk_ids=approved_ids,
            rejected_chunk_ids=rejected_chunk_ids,
            confidence=confidence,
            answer_intent=generated.answer_intent,
            diagnostics={
                "enough_evidence": workflow_result.enough_evidence,
                "prompt_version": generated.prompt_version,
                "model_name": generated.model_name,
                "retry_query": request.retry_query,
                **generated.diagnostics,
                **workflow_result.diagnostics,
            },
        )

    @staticmethod
    def _build_override_workflow_result(
        *,
        request: QuestionAnsweringRequest,
        analyzed_query: RetrievalQuery,
    ) -> RetrievalWorkflowResult:
        override_chunks = list(request.context_override_chunks or [])
        citations = [
            chunk.citation
            for chunk in override_chunks
            if isinstance(chunk.citation, Citation)
        ]
        retrieval_result = RetrievalResult(
            result_id=new_id("rr"),
            query=analyzed_query,
            chunks=override_chunks,
            citations=citations,
            total_candidates=len(override_chunks),
        )
        diagnostics: dict[str, object] = {
            "context_override_used": True,
        }
        if request.retry_query:
            diagnostics["retry_query"] = request.retry_query
        return RetrievalWorkflowResult(
            retrieval_result=retrieval_result,
            enough_evidence=retrieval_result.has_enough_evidence(1),
            min_evidence_chunks=1,
            context_chunks=override_chunks,
            diagnostics=diagnostics,
        )

    @staticmethod
    def _document_scope_violation(
        *,
        approved_chunks: list,
        document_id: str | None,
    ) -> GuardrailResult | None:
        if document_id is None:
            return None

        leaking_chunks = [
            chunk for chunk in approved_chunks if chunk.document_id != document_id
        ]
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

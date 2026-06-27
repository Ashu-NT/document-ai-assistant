from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.guardrails.guardrail_runner import GuardrailRunner
from src.application.guardrails.context.context_guardrail_chain import ContextGuardrailChain
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
from src.domain.retrieval import RetrievalQuery

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
        answer_generation_service: AnswerGenerationService | None = None,
        post_answer_guardrails: list[Guardrail] | None = None,
    ) -> None:
        self._retrieval_workflow = retrieval_workflow
        self._exploration_service = exploration_service
        self._router = router or QuestionAnsweringRouter()
        self._pre_query_guardrails: list[Guardrail] = pre_query_guardrails or []
        self._context_guardrail_chain = ContextGuardrailChain(context_guardrails or [])
        self._answer_generation_service = answer_generation_service
        self._post_answer_guardrails: list[Guardrail] = post_answer_guardrails or []

    def run(self, request: QuestionAnsweringRequest) -> QuestionAnsweringResult:
        allow_generation = request.allow_answer_generation

        if self._pre_query_guardrails:
            context = GuardrailContext(query_text=request.question)
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

        route, analyzed_query = self._router.decide(
            question=request.question,
            top_k=request.top_k or 5,
        )

        if route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION:
            return self._handle_exploration(request)

        return self._handle_retrieval(request, analyzed_query, allow_generation)

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
        allow_generation: bool = False,
    ) -> QuestionAnsweringResult:
        workflow_result = self._retrieval_workflow.run(analyzed_query)

        # Phase 4: context guardrails — filter, budget, quality
        approved_chunks, context_blocking = self._context_guardrail_chain.run(
            retrieved_chunks=workflow_result.final_chunks,
            query_text=request.question,
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
                diagnostics={"enough_evidence": workflow_result.enough_evidence},
            )

        if self._answer_generation_service is None:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.RETRIEVAL_QA,
                answer_text=_ANSWER_GENERATION_NOT_CONFIGURED_MESSAGE,
                retrieval_result=workflow_result,
                approved_chunk_ids=approved_ids,
                rejected_chunk_ids=rejected_chunk_ids,
                confidence=confidence,
                diagnostics={"enough_evidence": workflow_result.enough_evidence},
            )

        # LLM only ever sees approved_chunks
        gen_request = AnswerGenerationRequest(
            question=request.question,
            context_chunks=approved_chunks,
            query_intent=analyzed_query.chunk_types[0].value if analyzed_query.chunk_types else None,
            document_id=request.document_id,
            require_citations=request.require_citations,
        )
        generated = self._answer_generation_service.generate(gen_request)

        # Phase 6: post-answer guardrails
        if self._post_answer_guardrails:
            post_context = GuardrailContext(
                query_text=request.question,
                approved_chunks=approved_chunks,
                answer_text=generated.answer_text,
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
            diagnostics={
                "enough_evidence": workflow_result.enough_evidence,
                "prompt_version": generated.prompt_version,
                "model_name": generated.model_name,
            },
        )

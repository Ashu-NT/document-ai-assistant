from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.guardrails.guardrail_runner import GuardrailRunner
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


class QuestionAnsweringWorkflow:
    def __init__(
        self,
        retrieval_workflow: RetrievalWorkflow,
        exploration_service: DocumentExplorationService,
        router: QuestionAnsweringRouter | None = None,
        pre_query_guardrails: list[Guardrail] | None = None,
    ) -> None:
        self._retrieval_workflow = retrieval_workflow
        self._exploration_service = exploration_service
        self._router = router or QuestionAnsweringRouter()
        self._pre_query_guardrails: list[Guardrail] = pre_query_guardrails or []

    def run(self, request: QuestionAnsweringRequest) -> QuestionAnsweringResult:
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

        return self._handle_retrieval(request, analyzed_query)

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
    ) -> QuestionAnsweringResult:
        workflow_result = self._retrieval_workflow.run(analyzed_query)

        guardrail_result = workflow_result.guardrail_result
        rejected_chunk_ids: list[str] = (
            list(guardrail_result.rejected_chunk_ids) if guardrail_result else []
        )
        rejected_set = set(rejected_chunk_ids)
        approved_chunk_ids = [
            c.chunk_id
            for c in workflow_result.final_chunks
            if c.chunk_id not in rejected_set
        ]

        best_score = workflow_result.retrieval_result.best_score()
        confidence = str(round(best_score, 4)) if best_score is not None else None

        # Citations are populated by the answer generation stage (not yet implemented).
        # When AnswerGenerationService is introduced, it will populate citations from
        # grounded evidence and write them back into this result.
        answer_text = (
            _ANSWER_GENERATION_DISABLED_MESSAGE
            if not request.allow_answer_generation
            else None
        )

        return QuestionAnsweringResult(
            route=QuestionAnsweringRoute.RETRIEVAL_QA,
            answer_text=answer_text,
            guardrail_result=guardrail_result,
            guardrail_decision=guardrail_result.decision if guardrail_result else None,
            retrieval_result=workflow_result,
            approved_chunk_ids=approved_chunk_ids,
            rejected_chunk_ids=rejected_chunk_ids,
            confidence=confidence,
            diagnostics={"enough_evidence": workflow_result.enough_evidence},
        )

from typing import Callable

from src.application.contracts.guardrails.guardrail import Guardrail
from src.application.contracts.guardrails.guardrail_context import GuardrailContext
from src.application.contracts.guardrails.guardrail_decision import GuardrailDecision
from src.application.guardrails.guardrail_runner import GuardrailRunner
from src.application.guardrails.context.context_guardrail_chain import ContextGuardrailChain
from src.application.guardrails.services import PreGenerationGuardrailService
from src.application.services.answer_generation.answer_generation_service import (
    AnswerGenerationService,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
)
from src.application.services.document import DocumentLookupService
from src.application.services.document_exploration.document_exploration_service import (
    DocumentExplorationService,
    DocumentNotFoundError,
)
from src.application.workflows.question_answering.answer_context.answer_context_organizer import (
    AnswerContextOrganizer,
)
from src.application.workflows.question_answering.answer_context.structured_evidence_view_builder import (
    StructuredEvidenceViewBuilder,
)
from src.application.workflows.question_answering.answer_context.structured_fact_key_value_builder import (
    StructuredFactKeyValueBuilder,
)
from src.application.workflows.question_answering.answer_pipeline.answer_generation_pipeline import (
    AnswerGenerationPipeline,
)
from src.application.workflows.question_answering.answer_pipeline.override_workflow_result_builder import (
    build_override_workflow_result,
)
from src.application.workflows.question_answering.answer_pipeline.structured_evidence_merger import (
    StructuredEvidenceMerger,
)
from src.application.workflows.question_answering.answer_pipeline.structured_fact_join.structured_fact_joiner import (
    StructuredFactJoiner,
)
from src.application.workflows.question_answering.evidence import (
    FinalEvidencePreparer,
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
from src.application.workflows.retrieval.structured import StructuredEvidenceResolver
from src.domain.retrieval import RetrievalQuery
from src.shared.progress.progress_emitter import emit_progress


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
        document_lookup_service: DocumentLookupService | None = None,
        answer_context_organizer: AnswerContextOrganizer | None = None,
        structured_fact_key_value_builder: StructuredFactKeyValueBuilder | None = None,
        structured_evidence_view_builder: StructuredEvidenceViewBuilder | None = None,
        final_evidence_preparer: FinalEvidencePreparer | None = None,
        structured_evidence_resolver: StructuredEvidenceResolver | None = None,
        answer_intent_analyzer: AnswerIntentAnalyzer | None = None,
    ) -> None:
        self._retrieval_workflow = retrieval_workflow
        self._exploration_service = exploration_service
        self._router = router or QuestionAnsweringRouter()
        self._pre_query_guardrails: list[Guardrail] = pre_query_guardrails or []

        structured_fact_joiner = StructuredFactJoiner(
            document_lookup_service=document_lookup_service,
            final_evidence_preparer=final_evidence_preparer
            or FinalEvidencePreparer(document_lookup_service=document_lookup_service),
            answer_context_organizer=answer_context_organizer or AnswerContextOrganizer(),
            structured_fact_key_value_builder=(
                structured_fact_key_value_builder or StructuredFactKeyValueBuilder()
            ),
            structured_evidence_view_builder=(
                structured_evidence_view_builder or StructuredEvidenceViewBuilder()
            ),
            answer_intent_analyzer=answer_intent_analyzer or AnswerIntentAnalyzer(),
        )
        self._answer_generation_pipeline = AnswerGenerationPipeline(
            context_guardrail_chain=ContextGuardrailChain(context_guardrails or []),
            pre_generation_guardrail_service=(
                pre_generation_guardrail_service or PreGenerationGuardrailService()
            ),
            answer_generation_service=answer_generation_service,
            post_answer_guardrails=post_answer_guardrails or [],
            structured_evidence_merger=StructuredEvidenceMerger(
                structured_evidence_resolver
            ),
            structured_fact_joiner=structured_fact_joiner,
        )

    def run(
        self,
        request: QuestionAnsweringRequest,
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> QuestionAnsweringResult:
        allow_generation = request.allow_answer_generation

        if self._pre_query_guardrails:
            emit_progress(progress_callback, "Checking guardrails...")
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

        emit_progress(progress_callback, "Analyzing question...")
        route, analyzed_query, analyzed_intent = self._router.decide(
            question=request.question,
            top_k=request.top_k or 5,
            document_id=request.document_id,
        )

        if route == QuestionAnsweringRoute.DOCUMENT_EXPLORATION:
            return self._handle_exploration(request, progress_callback=progress_callback)

        if request.context_override_chunks is not None:
            workflow_result = build_override_workflow_result(
                request=request,
                analyzed_query=analyzed_query,
            )
            return self._answer_generation_pipeline.run(
                request=request,
                analyzed_query=analyzed_query,
                analyzed_intent=analyzed_intent,
                allow_generation=allow_generation,
                workflow_result=workflow_result,
                progress_callback=progress_callback,
            )

        return self._handle_retrieval(
            request,
            analyzed_query,
            analyzed_intent.value,
            allow_generation,
            progress_callback=progress_callback,
        )

    def _handle_exploration(
        self,
        request: QuestionAnsweringRequest,
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> QuestionAnsweringResult:
        if not request.document_id:
            return QuestionAnsweringResult(
                route=QuestionAnsweringRoute.DOCUMENT_EXPLORATION,
                safe_user_message="Please specify a document to explore.",
                diagnostics={"reason": "missing_document_id"},
            )

        emit_progress(progress_callback, "Exploring document...")
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
        *,
        progress_callback: Callable[[str], None] | None = None,
    ) -> QuestionAnsweringResult:
        emit_progress(progress_callback, "Retrieving evidence...")
        workflow_result = self._retrieval_workflow.run(analyzed_query)
        emit_progress(
            progress_callback,
            f"Retrieved {len(workflow_result.final_chunks)} evidence chunk(s).",
        )
        return self._answer_generation_pipeline.run(
            request=request,
            analyzed_query=analyzed_query,
            analyzed_intent=analyzed_intent,
            allow_generation=allow_generation,
            workflow_result=workflow_result,
            progress_callback=progress_callback,
        )

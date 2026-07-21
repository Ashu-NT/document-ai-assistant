from dataclasses import replace

from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.formatting.policy.answer_format_policy import (
    AnswerFormatPolicy,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
    AnswerIntentDecision,
)
from src.application.workflows.question_answering.answer_context.answer_context_organizer import (
    AnswerContextOrganizer,
)
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


class AnswerGenerationRequestResolver:
    """Normalizes an incoming AnswerGenerationRequest before generation:
    resolves the answer intent (reusing an upstream-provided decision when
    available), organizes structured_context when the caller didn't already
    build one, and resolves the format policy -- producing the fully
    resolved request plus the intent decision used to build it."""

    def __init__(
        self,
        answer_intent_analyzer: AnswerIntentAnalyzer,
        answer_context_organizer: AnswerContextOrganizer,
    ) -> None:
        self.answer_intent_analyzer = answer_intent_analyzer
        self.answer_context_organizer = answer_context_organizer

    def resolve(
        self,
        request: AnswerGenerationRequest,
    ) -> tuple[AnswerGenerationRequest, AnswerIntentDecision]:
        context_chunks = request.context_chunks

        intent_decision = self._resolve_intent_decision(
            request=request,
            context_chunks=context_chunks,
        )
        answer_intent = request.answer_intent or intent_decision.intent
        structured_context = request.structured_context
        if structured_context is None:
            structured_context = self.answer_context_organizer.organize(
                answer_intent=answer_intent,
                chunks=context_chunks,
                resolved_identifiers=request.resolved_identifiers,
            )
        elif structured_context.answer_intent != answer_intent:
            structured_context = replace(
                structured_context,
                answer_intent=answer_intent,
            )

        format_policy = request.format_policy or AnswerFormatPolicy.resolve(
            intent=answer_intent,
            structured_context=structured_context,
        )
        resolved_request = replace(
            request,
            context_chunks=context_chunks,
            answer_intent=answer_intent,
            structured_context=structured_context,
            format_policy=format_policy,
        )
        return resolved_request, intent_decision

    def _resolve_intent_decision(
        self,
        *,
        request: AnswerGenerationRequest,
        context_chunks: list[RetrievedChunk],
    ) -> AnswerIntentDecision:
        # An upstream caller (QuestionAnsweringWorkflow) that already built
        # structured_context has necessarily already run analyze() once to
        # decide what to extract into it. Reusing that decision instead of
        # calling analyze() again here removes a second, redundant
        # AnswerIntentAnalyzer computation (previously via a second
        # AnswerIntentAnalyzer instance) per answer, and closes off the
        # possibility of the two computations disagreeing (they always used
        # the same inputs today, but nothing enforced that).
        if request.answer_intent_decision is not None:
            return request.answer_intent_decision
        return self.answer_intent_analyzer.analyze(
            question=request.question,
            retrieval_intent=request.retrieval_intent,
            chunk_type_preferences=request.chunk_type_preferences,
            approved_chunks=context_chunks,
            legacy_query_intent=request.query_intent,
            route=request.route,
        )

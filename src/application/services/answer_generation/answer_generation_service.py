from dataclasses import replace

from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION, AnswerPromptBuilder
from src.application.services.ai.llm_service import LLMService
from src.application.services.answer_generation.formatting.answer_format_policy import (
    AnswerFormatPolicy,
)
from src.application.services.answer_generation.formatting.identifier_answer_renderer import (
    IdentifierAnswerRenderer,
)
from src.application.services.answer_generation.formatting.spare_parts_list_renderer import (
    SparePartsListRenderer,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
    AnswerIntentDecision,
)
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)
from src.application.workflows.question_answering.answer_context.answer_context_organizer import (
    AnswerContextOrganizer,
)
from src.domain.common.processing_metadata import ModelProcessingMetadata
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action


def _default_answer_generation_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_llm or llm_settings.general_llm
    except Exception:
        return None


class AnswerGenerationService:
    def __init__(
        self,
        llm_service: LLMService,
        prompt_builder: AnswerPromptBuilder | None = None,
        answer_intent_analyzer: AnswerIntentAnalyzer | None = None,
        answer_context_organizer: AnswerContextOrganizer | None = None,
        identifier_answer_renderer: IdentifierAnswerRenderer | None = None,
        spare_parts_list_renderer: SparePartsListRenderer | None = None,
        answer_generation_model: str | None = None,
    ) -> None:
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder or AnswerPromptBuilder()
        self.answer_intent_analyzer = answer_intent_analyzer or AnswerIntentAnalyzer()
        self.answer_context_organizer = (
            answer_context_organizer or AnswerContextOrganizer()
        )
        self.identifier_answer_renderer = (
            identifier_answer_renderer or IdentifierAnswerRenderer()
        )
        self.spare_parts_list_renderer = (
            spare_parts_list_renderer or SparePartsListRenderer()
        )
        self.answer_generation_model = (
            answer_generation_model or _default_answer_generation_model()
        )

    @tracked_action(
        action="answer_generation.generated",
        entity_type="answer",
        activity=True,
        audit=False,
        event=False,
    )
    def generate(
        self,
        request: AnswerGenerationRequest,
        activity_context: ActivityContext | None = None,
    ) -> GeneratedAnswer:
        resolved_request, intent_decision = self._resolve_request(request)
        prompt_version = getattr(
            self.prompt_builder,
            "prompt_version",
            ANSWER_PROMPT_VERSION,
        )
        citations, cited_chunk_ids = self._build_citations(resolved_request.context_chunks)
        structured_context = resolved_request.structured_context
        maintenance_diagnostics = self._maintenance_diagnostics(structured_context)
        diagnostics = self._build_diagnostics(
            resolved_request=resolved_request,
            intent_decision=intent_decision,
            structured_context=structured_context,
            maintenance_diagnostics=maintenance_diagnostics,
        )
        deterministic_answer = self.identifier_answer_renderer.render(
            question=resolved_request.question,
            answer_intent=resolved_request.answer_intent,
            structured_context=structured_context,
            resolved_identifiers=resolved_request.resolved_identifiers,
        )
        deterministic_renderer_name = "identifier_answer_renderer"
        if deterministic_answer is None:
            deterministic_answer = self.spare_parts_list_renderer.render(
                question=resolved_request.question,
                answer_intent=resolved_request.answer_intent,
                chunks=resolved_request.context_chunks,
            )
            deterministic_renderer_name = "spare_parts_list_renderer"
        if deterministic_answer is not None:
            model_name = (
                "deterministic_identifier_renderer"
                if deterministic_renderer_name == "identifier_answer_renderer"
                else "deterministic_spare_parts_renderer"
            )
            return self._build_generated_answer(
                answer_text=deterministic_answer,
                citations=citations,
                cited_chunk_ids=cited_chunk_ids,
                prompt_version=prompt_version,
                model_name=model_name,
                answer_intent=resolved_request.answer_intent,
                confidence=intent_decision.confidence,
                diagnostics={
                    **diagnostics,
                    "deterministic_renderer": deterministic_renderer_name,
                },
            )

        prompt = self.prompt_builder.build(resolved_request)
        raw_output = self.llm_service.generate(prompt, model=self.answer_generation_model)
        model_name = self.answer_generation_model or "default"

        return self._build_generated_answer(
            answer_text=raw_output,
            citations=citations,
            cited_chunk_ids=cited_chunk_ids,
            prompt_version=prompt_version,
            model_name=model_name,
            answer_intent=resolved_request.answer_intent,
            confidence=intent_decision.confidence,
            diagnostics=diagnostics,
        )

    @staticmethod
    def _build_citations(
        chunks: list[RetrievedChunk],
    ) -> tuple[list[Citation], list[str]]:
        citations: list[Citation] = []
        cited_chunk_ids: list[str] = []
        for chunk in chunks:
            if chunk.citation is not None:
                citations.append(chunk.citation)
                cited_chunk_ids.append(chunk.chunk_id)
        return citations, cited_chunk_ids

    def _resolve_request(
        self,
        request: AnswerGenerationRequest,
    ) -> tuple[AnswerGenerationRequest, AnswerIntentDecision]:
        context_chunks = request.context_chunks
        if request.max_context_chunks is not None:
            context_chunks = context_chunks[: request.max_context_chunks]

        intent_decision = self.answer_intent_analyzer.analyze(
            question=request.question,
            retrieval_intent=request.retrieval_intent,
            chunk_type_preferences=request.chunk_type_preferences,
            approved_chunks=context_chunks,
            legacy_query_intent=request.query_intent,
            route=request.route,
        )
        answer_intent = request.answer_intent or intent_decision.intent
        structured_context = request.structured_context
        if structured_context is None:
            structured_context = self.answer_context_organizer.organize(
                answer_intent=answer_intent,
                chunks=context_chunks,
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

    @staticmethod
    def _maintenance_diagnostics(
        structured_context,
    ) -> dict[str, int]:
        if structured_context is None:
            return {
                "maintenance_items_found": 0,
                "maintenance_items_with_interval": 0,
                "maintenance_items_without_interval": 0,
                "maintenance_items_merged": 0,
            }
        diagnostics = structured_context.diagnostics
        return {
            "maintenance_items_found": int(
                diagnostics.get("maintenance_items_found", 0)
            ),
            "maintenance_items_with_interval": int(
                diagnostics.get("maintenance_items_with_interval", 0)
            ),
            "maintenance_items_without_interval": int(
                diagnostics.get("maintenance_items_without_interval", 0)
            ),
            "maintenance_items_merged": int(
                diagnostics.get("maintenance_items_merged", 0)
            ),
        }

    @staticmethod
    def _build_diagnostics(
        *,
        resolved_request: AnswerGenerationRequest,
        intent_decision: AnswerIntentDecision,
        structured_context,
        maintenance_diagnostics: dict[str, int],
    ) -> dict[str, object]:
        return {
            "answer_intent": (
                resolved_request.answer_intent.value
                if resolved_request.answer_intent is not None
                else None
            ),
            "answer_intent_confidence": intent_decision.confidence,
            "answer_intent_reason": intent_decision.reason,
            "answer_intent_signals": intent_decision.matched_signals,
            "format_policy": (
                resolved_request.format_policy.preferred_format
                if resolved_request.format_policy is not None
                else None
            ),
            "structured_context_source_count": (
                structured_context.source_count if structured_context is not None else 0
            ),
            **maintenance_diagnostics,
        }

    @staticmethod
    def _build_generated_answer(
        *,
        answer_text: str,
        citations: list[Citation],
        cited_chunk_ids: list[str],
        prompt_version: str,
        model_name: str,
        answer_intent,
        confidence: float,
        diagnostics: dict[str, object],
    ) -> GeneratedAnswer:
        return GeneratedAnswer(
            answer_text=answer_text,
            citations=citations,
            cited_chunk_ids=cited_chunk_ids,
            prompt_version=prompt_version,
            model_name=model_name,
            confidence=confidence,
            raw_model_output=answer_text,
            metadata=ModelProcessingMetadata(
                model_name=model_name,
                model_type="answer_generation",
                confidence=confidence,
                prompt_version=prompt_version,
            ),
            answer_intent=answer_intent,
            diagnostics=diagnostics,
        )

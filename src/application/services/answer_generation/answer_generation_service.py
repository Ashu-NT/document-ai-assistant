from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION, AnswerPromptBuilder
from src.application.services.ai.llm_service import LLMService
from src.application.services.answer_generation.answer_generation_diagnostics_builder import (
    build_generation_diagnostics,
    build_maintenance_diagnostics,
)
from src.application.services.answer_generation.formatting.identifier_answer_renderer import (
    IdentifierAnswerRenderer,
)
from src.application.services.answer_generation.formatting.spare_parts_list_renderer import (
    SparePartsListRenderer,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
)
from src.application.services.answer_generation.answer_generation_request import (
    AnswerGenerationRequest,
)
from src.application.services.answer_generation.answer_generation_request_resolver import (
    AnswerGenerationRequestResolver,
)
from src.application.services.answer_generation.answer_generation_response_parser import (
    AnswerGenerationResponseParser,
)
from src.application.services.answer_generation.answer_generation_response_schema import (
    AnswerSectionPayload,
    ReferenceNotePayload,
    build_answer_generation_response_json_schema,
)
from src.application.services.answer_generation.answer_generation_result import (
    AnswerSection,
    GeneratedAnswer,
    ReferenceNote,
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
        response_parser: AnswerGenerationResponseParser | None = None,
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
        self.response_parser = response_parser or AnswerGenerationResponseParser()
        self.answer_generation_model = (
            answer_generation_model or _default_answer_generation_model()
        )
        self.request_resolver = AnswerGenerationRequestResolver(
            answer_intent_analyzer=self.answer_intent_analyzer,
            answer_context_organizer=self.answer_context_organizer,
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
        resolved_request, intent_decision = self.request_resolver.resolve(request)
        prompt_version = getattr(
            self.prompt_builder,
            "prompt_version",
            ANSWER_PROMPT_VERSION,
        )
        citations, cited_chunk_ids = self._build_citations(resolved_request.context_chunks)
        structured_context = resolved_request.structured_context
        maintenance_diagnostics = build_maintenance_diagnostics(structured_context)
        diagnostics = build_generation_diagnostics(
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
                sources=structured_context.sources if structured_context is not None else (),
                resolved_structured_entities=resolved_request.resolved_structured_entities,
            )
            deterministic_renderer_name = "spare_parts_list_renderer"
        if deterministic_answer is not None:
            model_name = (
                "deterministic_identifier_renderer"
                if deterministic_renderer_name == "identifier_answer_renderer"
                else "deterministic_spare_parts_renderer"
            )
            deterministic_diagnostics = {"deterministic_renderer": deterministic_renderer_name}
            if deterministic_renderer_name == "spare_parts_list_renderer":
                deterministic_diagnostics.update(
                    self.spare_parts_list_renderer.last_diagnostics()
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
                    **deterministic_diagnostics,
                },
                raw_model_output=deterministic_answer,
            )

        prompt = self.prompt_builder.build(resolved_request)
        raw_output = self.llm_service.generate(
            prompt,
            model=self.answer_generation_model,
            response_schema=build_answer_generation_response_json_schema(),
        )
        parsed_output = self.response_parser.parse(raw_output)
        model_name = self.answer_generation_model or "default"
        sources = structured_context.sources if structured_context is not None else ()

        return self._build_generated_answer(
            answer_text=parsed_output.answer_text,
            citations=citations,
            cited_chunk_ids=cited_chunk_ids,
            prompt_version=prompt_version,
            model_name=model_name,
            answer_intent=resolved_request.answer_intent,
            confidence=intent_decision.confidence,
            diagnostics=diagnostics,
            raw_model_output=raw_output,
            limitation_note=parsed_output.limitation_note,
            sections=self._resolve_sections(parsed_output.sections),
            reference_notes=self._resolve_reference_notes(
                parsed_output.reference_notes, sources
            ),
        )

    @staticmethod
    def _resolve_sections(
        payload_sections: list[AnswerSectionPayload],
    ) -> list[AnswerSection]:
        return [
            AnswerSection(
                heading=section.heading,
                body=section.body,
                reference_note_ids=list(section.reference_note_ids),
            )
            for section in payload_sections
        ]

    @staticmethod
    def _resolve_reference_notes(
        payload_notes: list[ReferenceNotePayload],
        sources,
    ) -> list[ReferenceNote]:
        chunk_id_by_source_number = {
            source.source_number: source.chunk_id for source in sources
        }
        return [
            ReferenceNote(
                note_id=note.note_id,
                claim_text=note.claim_text,
                source_number=note.source_number,
                chunk_id=chunk_id_by_source_number.get(note.source_number),
            )
            for note in payload_notes
        ]

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
        raw_model_output: str,
        limitation_note: str | None = None,
        sections: list[AnswerSection] | None = None,
        reference_notes: list[ReferenceNote] | None = None,
    ) -> GeneratedAnswer:
        return GeneratedAnswer(
            answer_text=answer_text,
            citations=citations,
            cited_chunk_ids=cited_chunk_ids,
            prompt_version=prompt_version,
            model_name=model_name,
            confidence=confidence,
            metadata=ModelProcessingMetadata(
                model_name=model_name,
                model_type="answer_generation",
                confidence=confidence,
                prompt_version=prompt_version,
            ),
            answer_intent=answer_intent,
            diagnostics=diagnostics,
            raw_model_output=raw_model_output,
            limitation_note=limitation_note,
            sections=sections or [],
            reference_notes=reference_notes or [],
        )

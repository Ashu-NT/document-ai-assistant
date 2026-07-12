from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION, AnswerPromptBuilder
from src.application.services.ai.llm_service import LLMService
from src.application.services.answer_generation.answer_generation_diagnostics_builder import (
    build_generation_diagnostics,
    build_maintenance_diagnostics,
)
from src.application.services.answer_generation.formatting.identifier_answer_renderer import (
    IdentifierAnswerRenderer,
)
from src.application.services.answer_generation.formatting.renderers import (
    DeterministicAnswerRendererDispatcher,
    KeyValueFactSheetRenderer,
    MaintenanceScheduleRenderer,
    ProcedureStepsRenderer,
    TroubleshootingRenderer,
)
from src.application.services.answer_generation.formatting.spare_parts_list_renderer import (
    SparePartsListRenderer,
)
from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
)
from src.application.services.answer_generation.intent.answer_intent_vocabulary import (
    CERTIFICATION_TERMS,
    DOCUMENT_SUMMARY_TERMS,
    IDENTIFIER_TERMS,
    MAINTENANCE_TERMS,
    PROCEDURE_TERMS,
    SAFETY_TERMS,
    SPECIFICATION_TERMS,
    TABLE_TERMS,
    TROUBLESHOOTING_TERMS,
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
    AnswerGenerationResponsePayload,
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
from src.config.logging import get_logger
from src.domain.common.processing_metadata import ModelProcessingMetadata
from src.domain.retrieval.citation import Citation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk
from src.shared.activity import ActivityContext
from src.shared.exceptions import SchemaValidationError
from src.shared.execution import tracked_action

_logger = get_logger(__name__)

# Bounded retry-with-repair for malformed/schema-invalid LLM JSON (finding
# 3.1): 1 original attempt + 1 corrective retry. Mirrors the extraction
# pipeline's ExtractionBatchRetryCoordinator shape, adapted to this
# service's single-call (not batched) generation. Deliberately a small
# hardcoded constant, not a settings-driven value -- nothing asked for
# per-deployment tuning of this number.
_MAX_GENERATION_ATTEMPTS = 2

# Conservative, cheap compound-question signal for finding 3.3: a
# deterministic renderer can silently answer only half of a compound
# question. Only the 3 explicit conjunction phrases below are treated as a
# clause boundary -- no broader NLP splitting.
_COMPOUND_CONJUNCTIONS = (" and ", " also ", " as well as ")

# Reuses the EXISTING keyword vocabulary from answer_intent_vocabulary.py
# (no new keyword list invented) so each half of a compound question can be
# checked against the other intent categories' term sets.
_INTENT_TERM_SETS: dict[AnswerIntent, tuple[str, ...]] = {
    AnswerIntent.SPECIFICATION_SUMMARY: SPECIFICATION_TERMS,
    AnswerIntent.MAINTENANCE_SUMMARY: MAINTENANCE_TERMS,
    AnswerIntent.PROCEDURE_STEPS: PROCEDURE_TERMS,
    AnswerIntent.SAFETY_WARNINGS: SAFETY_TERMS,
    AnswerIntent.TROUBLESHOOTING: TROUBLESHOOTING_TERMS,
    AnswerIntent.CERTIFICATION_SUMMARY: CERTIFICATION_TERMS,
    AnswerIntent.IDENTIFIER_LOOKUP: IDENTIFIER_TERMS,
    AnswerIntent.TABLE_SUMMARY: TABLE_TERMS,
    AnswerIntent.DOCUMENT_SUMMARY: DOCUMENT_SUMMARY_TERMS,
}

# IDENTIFIER_LOOKUP and TABLE_SUMMARY are not "a different, unrelated"
# category from each other for this check -- SparePartsListRenderer
# already deterministically answers both, and TABLE_TERMS' bare "list"
# would otherwise false-positive on ordinary identifier-listing questions
# (e.g. "list all serial and part numbers"). Excluding the sibling
# category keeps the signal conservative rather than noisy.
_COMPOUND_EXCLUDED_INTENTS_BY_DRIVING: dict[AnswerIntent, frozenset[AnswerIntent]] = {
    AnswerIntent.IDENTIFIER_LOOKUP: frozenset(
        {AnswerIntent.IDENTIFIER_LOOKUP, AnswerIntent.TABLE_SUMMARY}
    ),
    AnswerIntent.TABLE_SUMMARY: frozenset(
        {AnswerIntent.IDENTIFIER_LOOKUP, AnswerIntent.TABLE_SUMMARY}
    ),
}

_RENDERER_LIMITATION_LABELS: dict[str, str] = {
    "identifier_answer_renderer": "identifier",
    "spare_parts_list_renderer": "spare parts",
    "maintenance_schedule_renderer": "maintenance schedule",
    "procedure_steps_renderer": "procedure steps",
    "troubleshooting_renderer": "troubleshooting guidance",
    "key_value_fact_sheet_renderer": "structured facts",
}


def _default_answer_generation_model() -> str | None:
    try:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_llm or llm_settings.general_llm
    except Exception:
        _logger.warning(
            "answer_generation.settings_fallback setting=answer_generation_model "
            "fallback_value=%s",
            None,
        )
        return None


def _default_answer_generation_temperature() -> float:
    try:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_temperature
    except Exception:
        fallback = 0.2
        _logger.warning(
            "answer_generation.settings_fallback setting=answer_generation_temperature "
            "fallback_value=%s",
            fallback,
        )
        return fallback


def _default_answer_generation_num_ctx() -> int:
    try:
        from src.config.settings import llm_settings

        return llm_settings.answer_generation_num_ctx
    except Exception:
        fallback = 8192
        _logger.warning(
            "answer_generation.settings_fallback setting=answer_generation_num_ctx "
            "fallback_value=%s",
            fallback,
        )
        return fallback


def _default_capture_answer_prompt_text() -> bool:
    try:
        from src.config.settings import llm_settings

        return llm_settings.capture_answer_prompt_text
    except Exception:
        fallback = False
        _logger.warning(
            "answer_generation.settings_fallback setting=capture_answer_prompt_text "
            "fallback_value=%s",
            fallback,
        )
        return fallback


def _build_corrective_note(previous_error: str) -> str:
    """A minimal string suffix appended to the already-built prompt for the
    one corrective retry -- mirrors ExtractionBatchRetryCoordinator's
    "feed the previous error back into the next prompt" pattern, but kept
    local to this service rather than inside AnswerPromptBuilder (owned
    elsewhere)."""
    return (
        "\n\nYour previous response was rejected because it did not match "
        f"the required schema: {previous_error}\n"
        "Fix this specific problem and return a corrected JSON response "
        "that matches the schema exactly."
    )


def _detect_unrelated_intent_signal(
    question: str, driving_intent: AnswerIntent | None
) -> AnswerIntent | None:
    """Returns another intent category's signal if `question` looks like a
    compound question (joined by an explicit conjunction) whose other half
    scores toward a DIFFERENT, unrelated answer-intent category than the
    one driving the current deterministic-renderer path. Conservative by
    design: only 3 conjunction phrases, only existing vocabulary term
    membership, no scoring."""
    normalized = " " + " ".join((question or "").strip().lower().split()) + " "
    matched_conjunction = next(
        (conjunction for conjunction in _COMPOUND_CONJUNCTIONS if conjunction in normalized),
        None,
    )
    if matched_conjunction is None:
        return None

    left, _, right = normalized.partition(matched_conjunction)
    excluded_intents = _COMPOUND_EXCLUDED_INTENTS_BY_DRIVING.get(
        driving_intent,
        frozenset({driving_intent}) if driving_intent is not None else frozenset(),
    )
    for half in (left, right):
        for intent, terms in _INTENT_TERM_SETS.items():
            if intent in excluded_intents:
                continue
            if any(term in half for term in terms):
                return intent
    return None


def _build_compound_question_limitation_note(renderer_name: str) -> str:
    label = _RENDERER_LIMITATION_LABELS.get(renderer_name, "requested")
    return (
        f"This answer only addresses the {label} portion of your question "
        "— ask a follow-up for the rest."
    )


class AnswerGenerationService:
    def __init__(
        self,
        llm_service: LLMService,
        prompt_builder: AnswerPromptBuilder | None = None,
        answer_intent_analyzer: AnswerIntentAnalyzer | None = None,
        answer_context_organizer: AnswerContextOrganizer | None = None,
        identifier_answer_renderer: IdentifierAnswerRenderer | None = None,
        spare_parts_list_renderer: SparePartsListRenderer | None = None,
        maintenance_schedule_renderer: MaintenanceScheduleRenderer | None = None,
        procedure_steps_renderer: ProcedureStepsRenderer | None = None,
        troubleshooting_renderer: TroubleshootingRenderer | None = None,
        key_value_fact_sheet_renderer: KeyValueFactSheetRenderer | None = None,
        response_parser: AnswerGenerationResponseParser | None = None,
        answer_generation_model: str | None = None,
        answer_generation_temperature: float | None = None,
        answer_generation_num_ctx: int | None = None,
        capture_answer_prompt_text: bool | None = None,
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
        self.maintenance_schedule_renderer = (
            maintenance_schedule_renderer or MaintenanceScheduleRenderer()
        )
        self.procedure_steps_renderer = (
            procedure_steps_renderer or ProcedureStepsRenderer()
        )
        self.troubleshooting_renderer = (
            troubleshooting_renderer or TroubleshootingRenderer()
        )
        self.key_value_fact_sheet_renderer = (
            key_value_fact_sheet_renderer or KeyValueFactSheetRenderer()
        )
        self.response_parser = response_parser or AnswerGenerationResponseParser()
        self.deterministic_renderer_dispatcher = (
            DeterministicAnswerRendererDispatcher(
                identifier_answer_renderer=self.identifier_answer_renderer,
                spare_parts_list_renderer=self.spare_parts_list_renderer,
                maintenance_schedule_renderer=self.maintenance_schedule_renderer,
                procedure_steps_renderer=self.procedure_steps_renderer,
                troubleshooting_renderer=self.troubleshooting_renderer,
                key_value_fact_sheet_renderer=self.key_value_fact_sheet_renderer,
            )
        )
        self.answer_generation_model = (
            answer_generation_model or _default_answer_generation_model()
        )
        self.answer_generation_temperature = (
            answer_generation_temperature
            if answer_generation_temperature is not None
            else _default_answer_generation_temperature()
        )
        self.answer_generation_num_ctx = (
            answer_generation_num_ctx
            if answer_generation_num_ctx is not None
            else _default_answer_generation_num_ctx()
        )
        self.capture_answer_prompt_text = (
            capture_answer_prompt_text
            if capture_answer_prompt_text is not None
            else _default_capture_answer_prompt_text()
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
        deterministic_result = self.deterministic_renderer_dispatcher.render(
            question=resolved_request.question,
            answer_intent=resolved_request.answer_intent,
            structured_context=structured_context,
            resolved_identifiers=resolved_request.resolved_identifiers,
            resolved_structured_entities=resolved_request.resolved_structured_entities,
        )
        if deterministic_result is not None:
            deterministic_diagnostics = {
                "deterministic_renderer": deterministic_result.renderer_name,
                **deterministic_result.diagnostics,
            }
            unrelated_intent = _detect_unrelated_intent_signal(
                resolved_request.question, resolved_request.answer_intent
            )
            limitation_note = (
                _build_compound_question_limitation_note(
                    deterministic_result.renderer_name
                )
                if unrelated_intent is not None
                else None
            )
            return self._build_generated_answer(
                answer_text=deterministic_result.answer_text,
                citations=citations,
                cited_chunk_ids=cited_chunk_ids,
                prompt_version=prompt_version,
                model_name=deterministic_result.model_name,
                answer_intent=resolved_request.answer_intent,
                confidence=intent_decision.confidence,
                diagnostics={
                    **diagnostics,
                    **deterministic_diagnostics,
                },
                raw_model_output=deterministic_result.answer_text,
                limitation_note=limitation_note,
            )

        prompt = self.prompt_builder.build(resolved_request)
        if self.capture_answer_prompt_text:
            diagnostics["prompt_text"] = prompt
        parsed_output, raw_output = self._generate_and_parse(prompt)
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
                parsed_output.reference_notes,
                sources,
                appendix_source_numbers=self._appendix_source_numbers(),
            ),
        )

    def _generate_and_parse(
        self, prompt: str
    ) -> tuple[AnswerGenerationResponsePayload, str]:
        """Calls the LLM and parses its response, retrying once with a
        corrective note appended to the prompt if the first attempt's
        response is malformed/schema-invalid (finding 3.1). The parser
        itself already attempts a same-call JSON repair before raising, so
        this loop only covers the case where that repair still isn't
        enough -- at most `_MAX_GENERATION_ATTEMPTS` LLM calls total. If the
        final attempt still fails, the original SchemaValidationError type
        is re-raised unchanged (no fake success is synthesized)."""
        last_error: SchemaValidationError | None = None
        for attempt_index in range(1, _MAX_GENERATION_ATTEMPTS + 1):
            attempt_prompt = (
                prompt
                if last_error is None
                else prompt + _build_corrective_note(str(last_error))
            )
            raw_output = self.llm_service.generate(
                attempt_prompt,
                model=self.answer_generation_model,
                response_schema=build_answer_generation_response_json_schema(),
                temperature=self.answer_generation_temperature,
                num_ctx=self.answer_generation_num_ctx,
            )
            try:
                return self.response_parser.parse(raw_output), raw_output
            except SchemaValidationError as exc:
                last_error = exc
                if attempt_index >= _MAX_GENERATION_ATTEMPTS:
                    raise
        raise last_error  # pragma: no cover - unreachable safeguard

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

    def _appendix_source_numbers(self) -> set[int] | None:
        """The source_numbers that actually made it into the raw-prose
        appendix under RawSourceInclusionPolicy's budget, if the prompt
        builder in use exposes that (the real AnswerPromptBuilder does, via
        `last_context_bundle` set during `build()`). Returns None when this
        isn't available (e.g. a test double prompt builder, or no prompt
        was built at all on the deterministic-renderer paths) so callers
        can fall back to the pre-existing, unrestricted behavior instead of
        wrongly unresolving every citation.
        """
        bundle = getattr(self.prompt_builder, "last_context_bundle", None)
        if bundle is None:
            return None
        return set(bundle.appendix_source_numbers)

    @staticmethod
    def _resolve_reference_notes(
        payload_notes: list[ReferenceNotePayload],
        sources,
        *,
        appendix_source_numbers: set[int] | None = None,
    ) -> list[ReferenceNote]:
        chunk_id_by_source_number = {
            source.source_number: source.chunk_id
            for source in sources
            if appendix_source_numbers is None
            or source.source_number in appendix_source_numbers
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

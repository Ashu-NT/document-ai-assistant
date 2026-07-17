from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION, AnswerPromptBuilder
from src.application.services.ai.llm_service import LLMService
from src.application.services.answer_generation.answer_generation_diagnostics_builder import (
    build_generation_diagnostics,
    build_maintenance_diagnostics,
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
from src.application.services.answer_generation.answer_generation_result import (
    GeneratedAnswer,
)
from src.application.services.answer_generation.answer_generation_service_settings import (
    default_answer_generation_model,
    default_answer_generation_num_ctx,
    default_answer_generation_temperature,
    default_capture_answer_prompt_text,
)
from src.application.services.answer_generation.execution import (
    AnswerGenerationPromptExecutor,
    AnswerGenerationResultAssembler,
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
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
)
from src.application.services.answer_generation.intent.compound_question_limitation_resolver import (
    CompoundQuestionLimitationResolver,
)
from src.application.workflows.question_answering.answer_context.answer_context_organizer import (
    AnswerContextOrganizer,
)
from src.shared.activity import ActivityContext
from src.shared.execution import tracked_action


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
        self.answer_generation_model = (
            answer_generation_model or default_answer_generation_model()
        )
        self.answer_generation_temperature = (
            answer_generation_temperature
            if answer_generation_temperature is not None
            else default_answer_generation_temperature()
        )
        self.answer_generation_num_ctx = (
            answer_generation_num_ctx
            if answer_generation_num_ctx is not None
            else default_answer_generation_num_ctx()
        )
        self.capture_answer_prompt_text = (
            capture_answer_prompt_text
            if capture_answer_prompt_text is not None
            else default_capture_answer_prompt_text()
        )
        self.request_resolver = AnswerGenerationRequestResolver(
            answer_intent_analyzer=self.answer_intent_analyzer,
            answer_context_organizer=self.answer_context_organizer,
        )
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
        self.compound_question_limitation_resolver = (
            CompoundQuestionLimitationResolver()
        )
        self.prompt_executor = AnswerGenerationPromptExecutor(
            llm_service=self.llm_service,
            response_parser=self.response_parser,
            model_name=self.answer_generation_model,
            temperature=self.answer_generation_temperature,
            num_ctx=self.answer_generation_num_ctx,
        )
        self.result_assembler = AnswerGenerationResultAssembler(
            prompt_builder=self.prompt_builder
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
            show_raw_evidence=resolved_request.show_raw_evidence,
            structured_context=structured_context,
            resolved_identifiers=resolved_request.resolved_identifiers,
            resolved_structured_entities=resolved_request.resolved_structured_entities,
        )
        if deterministic_result is not None:
            return self._build_deterministic_answer(
                resolved_request=resolved_request,
                prompt_version=prompt_version,
                confidence=intent_decision.confidence,
                diagnostics=diagnostics,
                deterministic_result=deterministic_result,
            )

        prompt = self.prompt_builder.build(resolved_request)
        if self.capture_answer_prompt_text:
            diagnostics["prompt_text"] = prompt
        execution_result = self.prompt_executor.execute(prompt)
        sources = structured_context.sources if structured_context is not None else ()
        return self.result_assembler.build(
            answer_text=execution_result.parsed_output.answer_text,
            context_chunks=resolved_request.context_chunks,
            prompt_version=prompt_version,
            model_name=self.answer_generation_model or "default",
            answer_intent=resolved_request.answer_intent,
            confidence=intent_decision.confidence,
            diagnostics=diagnostics,
            raw_model_output=execution_result.raw_output,
            limitation_note=execution_result.parsed_output.limitation_note,
            payload=execution_result.parsed_output,
            sources=sources,
        )

    def _build_deterministic_answer(
        self,
        *,
        resolved_request,
        prompt_version: str,
        confidence: float,
        diagnostics: dict[str, object],
        deterministic_result,
    ) -> GeneratedAnswer:
        limitation_note = self.compound_question_limitation_resolver.limitation_note(
            question=resolved_request.question,
            driving_intent=resolved_request.answer_intent,
            renderer_name=deterministic_result.renderer_name,
        )
        return self.result_assembler.build(
            answer_text=deterministic_result.answer_text,
            context_chunks=resolved_request.context_chunks,
            prompt_version=prompt_version,
            model_name=deterministic_result.model_name,
            answer_intent=resolved_request.answer_intent,
            confidence=confidence,
            diagnostics={
                **diagnostics,
                "deterministic_renderer": deterministic_result.renderer_name,
                **deterministic_result.diagnostics,
            },
            raw_model_output=deterministic_result.answer_text,
            limitation_note=limitation_note,
        )

from src.application.prompts.answer_generation import ANSWER_PROMPT_VERSION, AnswerPromptBuilder
from src.application.prompts.answer_generation.prompt_context.appendix import (
    PromptBudgetAllocator,
    RawSourceAppendixFormatter,
    RawSourceInclusionPolicy,
)
from src.application.services.ai.llm_service import LLMService
from src.application.services.answer_generation.answer_generation_diagnostics_builder import (
    build_generation_diagnostics,
    build_maintenance_diagnostics,
    log_answer_generation_recorded,
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
from src.application.services.answer_generation.formatting.format_policy_violation_detector import (
    build_format_policy_corrective_note,
    detect_format_policy_violations,
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
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)
from src.application.services.answer_generation.intent.answer_intent_analyzer import (
    AnswerIntentAnalyzer,
)
from src.application.services.answer_generation.intent.compound_question_detector import (
    chunks_plausibly_cover_intent,
)
from src.application.services.answer_generation.intent.deterministic_dispatch_gate import (
    DeterministicDispatchGate,
    DispatchBypassReason,
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
        deterministic_dispatch_gate: DeterministicDispatchGate | None = None,
    ) -> None:
        self.llm_service = llm_service
        # Resolved before self.prompt_builder below so the default builder's
        # raw-source budget can scale with it (W5,
        # answering_flow_weakness_remediation_plan.md) -- an explicitly
        # injected prompt_builder is used as-is and is unaffected.
        self.answer_generation_num_ctx = (
            answer_generation_num_ctx
            if answer_generation_num_ctx is not None
            else default_answer_generation_num_ctx()
        )
        self.prompt_builder = prompt_builder or AnswerPromptBuilder(
            raw_source_appendix_formatter=RawSourceAppendixFormatter(
                raw_source_inclusion_policy=RawSourceInclusionPolicy(
                    prompt_budget_allocator=PromptBudgetAllocator(
                        num_ctx=self.answer_generation_num_ctx
                    )
                )
            )
        )
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
        self.deterministic_dispatch_gate = (
            deterministic_dispatch_gate or DeterministicDispatchGate()
        )
        self.prompt_executor = AnswerGenerationPromptExecutor(
            llm_service=self.llm_service,
            response_parser=self.response_parser,
            model_name=self.answer_generation_model,
            temperature=self.answer_generation_temperature,
            num_ctx=self.answer_generation_num_ctx,
        )
        self.result_assembler = AnswerGenerationResultAssembler()

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
        has_conflicting_evidence = bool(
            structured_context.diagnostics.get("has_critical_evidence_conflict")
        ) if structured_context is not None else False
        dispatch_gate_decision = self.deterministic_dispatch_gate.evaluate(
            question=resolved_request.question,
            effective_intent=resolved_request.answer_intent,
            intent_decision=intent_decision,
            has_conflicting_evidence=has_conflicting_evidence,
            retrieval_intent_contested=resolved_request.retrieval_intent_contested,
        )
        diagnostics["deterministic_dispatch_bypassed"] = (
            dispatch_gate_decision.should_bypass
        )
        diagnostics["deterministic_dispatch_bypass_reason"] = (
            dispatch_gate_decision.reason
        )
        if structured_context is not None:
            diagnostics["evidence_conflicts"] = structured_context.diagnostics.get(
                "evidence_conflicts", []
            )
        if dispatch_gate_decision.reason == DispatchBypassReason.COMPOUND_QUESTION:
            unrelated_intent = (
                AnswerIntent(dispatch_gate_decision.compound_intent_value)
                if dispatch_gate_decision.compound_intent_value is not None
                else None
            )
            diagnostics["compound_question_coverage_plausible"] = (
                chunks_plausibly_cover_intent(
                    resolved_request.context_chunks,
                    unrelated_intent,
                )
            )
        if not dispatch_gate_decision.should_bypass:
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

        # `build_with_context()` (not `build()`) returns the prompt-context
        # bundle directly, per this call, instead of the previous design of
        # caching it on `self.prompt_builder.last_context_bundle` --
        # unscoped mutable instance state that would have been a real
        # concurrency hazard under any future concurrent caller (finding
        # F10, outputs/architecture/answering_and_prompt_fresh_audit.md).
        prompt, context_bundle = self.prompt_builder.build_with_context(
            resolved_request
        )
        if self.capture_answer_prompt_text:
            diagnostics["prompt_text"] = prompt
        # Surface the canonicalizer's own truncation/omission counters --
        # previously computed onto the prompt-context bundle and then never
        # read by anything (finding F6).
        appendix_source_numbers = None
        if context_bundle is not None:
            diagnostics.update(context_bundle.diagnostics)
            appendix_source_numbers = set(context_bundle.appendix_source_numbers)
        execution_result = self.prompt_executor.execute(prompt)
        format_policy_violations = detect_format_policy_violations(
            format_policy=resolved_request.format_policy,
            answer_text=execution_result.parsed_output.answer_text,
        )
        format_policy_violation_regenerated = False
        if format_policy_violations:
            # Single corrective retry, structural violations only -- never
            # re-judges answer *content* (W7b,
            # answering_flow_weakness_remediation_plan.md). Mirrors
            # AnswerGenerationPromptExecutor's own schema-validation retry
            # shape: append a note describing exactly what was missing, ask
            # for one corrected attempt, accept whatever comes back
            # (a still-imperfect retry is still used -- this is a best
            # effort nudge, not a hard block).
            corrective_prompt = prompt + build_format_policy_corrective_note(
                format_policy_violations
            )
            execution_result = self.prompt_executor.execute(corrective_prompt)
            format_policy_violations = detect_format_policy_violations(
                format_policy=resolved_request.format_policy,
                answer_text=execution_result.parsed_output.answer_text,
            )
            format_policy_violation_regenerated = True
        diagnostics["format_policy_violation"] = bool(format_policy_violations)
        diagnostics["format_policy_violation_reasons"] = format_policy_violations
        diagnostics["format_policy_violation_regenerated"] = (
            format_policy_violation_regenerated
        )
        sources = structured_context.sources if structured_context is not None else ()
        log_answer_generation_recorded(
            answer_intent=resolved_request.answer_intent,
            diagnostics=diagnostics,
        )
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
            appendix_source_numbers=appendix_source_numbers,
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
        # No compound-question limitation_note here anymore: this method is
        # only reached when DeterministicDispatchGate already confirmed the
        # question isn't compound (finding F3) -- a renderer answer is
        # always the full answer now, not a partial one needing a
        # disclaimer.
        merged_diagnostics = {
            **diagnostics,
            "deterministic_renderer": deterministic_result.renderer_name,
            **deterministic_result.diagnostics,
        }
        log_answer_generation_recorded(
            answer_intent=resolved_request.answer_intent,
            diagnostics=merged_diagnostics,
        )
        return self.result_assembler.build(
            answer_text=deterministic_result.answer_text,
            context_chunks=resolved_request.context_chunks,
            prompt_version=prompt_version,
            model_name=deterministic_result.model_name,
            answer_intent=resolved_request.answer_intent,
            confidence=confidence,
            diagnostics=merged_diagnostics,
            raw_model_output=deterministic_result.answer_text,
        )

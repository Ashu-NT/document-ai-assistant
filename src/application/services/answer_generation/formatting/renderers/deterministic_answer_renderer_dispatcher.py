from __future__ import annotations

from src.application.services.answer_generation.formatting.identifier_answer_renderer import (
    IdentifierAnswerRenderer,
)
from src.application.services.answer_generation.formatting.renderers.deterministic_render_result import (
    DeterministicRenderResult,
)
from src.application.services.answer_generation.formatting.renderers.key_value_fact_sheet_renderer import (
    KeyValueFactSheetRenderer,
)
from src.application.services.answer_generation.formatting.renderers.maintenance_schedule_renderer import (
    MaintenanceScheduleRenderer,
)
from src.application.services.answer_generation.formatting.renderers.procedure_steps_renderer import (
    ProcedureStepsRenderer,
)
from src.application.services.answer_generation.formatting.renderers.troubleshooting_renderer import (
    TroubleshootingRenderer,
)
from src.application.services.answer_generation.formatting.spare_parts_list_renderer import (
    SparePartsListRenderer,
)
from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.domain.document.entities.identifier import Identifier


class DeterministicAnswerRendererDispatcher:
    def __init__(
        self,
        *,
        identifier_answer_renderer: IdentifierAnswerRenderer,
        spare_parts_list_renderer: SparePartsListRenderer,
        maintenance_schedule_renderer: MaintenanceScheduleRenderer,
        procedure_steps_renderer: ProcedureStepsRenderer,
        troubleshooting_renderer: TroubleshootingRenderer,
        key_value_fact_sheet_renderer: KeyValueFactSheetRenderer,
    ) -> None:
        self._identifier_answer_renderer = identifier_answer_renderer
        self._spare_parts_list_renderer = spare_parts_list_renderer
        self._maintenance_schedule_renderer = maintenance_schedule_renderer
        self._procedure_steps_renderer = procedure_steps_renderer
        self._troubleshooting_renderer = troubleshooting_renderer
        self._key_value_fact_sheet_renderer = key_value_fact_sheet_renderer

    def render(
        self,
        *,
        question: str,
        answer_intent: AnswerIntent | None,
        structured_context: StructuredAnswerContext | None,
        resolved_identifiers: list[Identifier],
        resolved_structured_entities: list[dict],
    ) -> DeterministicRenderResult | None:
        identifier_answer = self._identifier_answer_renderer.render(
            question=question,
            answer_intent=answer_intent,
            structured_context=structured_context,
            resolved_identifiers=resolved_identifiers,
        )
        if identifier_answer is not None:
            return DeterministicRenderResult(
                answer_text=identifier_answer,
                model_name="deterministic_identifier_renderer",
                renderer_name="identifier_answer_renderer",
            )

        spare_parts_answer = self._spare_parts_list_renderer.render(
            question=question,
            answer_intent=answer_intent,
            sources=structured_context.sources if structured_context is not None else (),
            resolved_structured_entities=resolved_structured_entities,
        )
        if spare_parts_answer is not None:
            return DeterministicRenderResult(
                answer_text=spare_parts_answer,
                model_name="deterministic_spare_parts_renderer",
                renderer_name="spare_parts_list_renderer",
                diagnostics=self._spare_parts_list_renderer.last_diagnostics(),
            )

        for answer_text, model_name, renderer_name in (
            (
                self._maintenance_schedule_renderer.render(
                    question=question,
                    answer_intent=answer_intent,
                    structured_context=structured_context,
                ),
                "deterministic_maintenance_schedule_renderer",
                "maintenance_schedule_renderer",
            ),
            (
                self._procedure_steps_renderer.render(
                    answer_intent=answer_intent,
                    structured_context=structured_context,
                ),
                "deterministic_procedure_steps_renderer",
                "procedure_steps_renderer",
            ),
            (
                self._troubleshooting_renderer.render(
                    answer_intent=answer_intent,
                    structured_context=structured_context,
                ),
                "deterministic_troubleshooting_renderer",
                "troubleshooting_renderer",
            ),
            (
                self._key_value_fact_sheet_renderer.render(
                    question=question,
                    answer_intent=answer_intent,
                    structured_context=structured_context,
                ),
                "deterministic_fact_sheet_renderer",
                "key_value_fact_sheet_renderer",
            ),
        ):
            if answer_text is not None:
                return DeterministicRenderResult(
                    answer_text=answer_text,
                    model_name=model_name,
                    renderer_name=renderer_name,
                )
        return None

from __future__ import annotations

from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)
from src.application.services.answer_generation.intent.answer_intent import (
    AnswerIntent,
)


class PromptEvidenceRoleAssigner:
    _TABLE_DIRECT_INTENTS = {
        AnswerIntent.TABLE_SUMMARY.value,
        AnswerIntent.SPECIFICATION_SUMMARY.value,
        AnswerIntent.CERTIFICATION_SUMMARY.value,
        AnswerIntent.IDENTIFIER_LOOKUP.value,
    }
    _PREFERRED_CHUNK_TYPES = {
        AnswerIntent.SPECIFICATION_SUMMARY.value: {"technical_specification"},
        AnswerIntent.MAINTENANCE_SUMMARY.value: {
            "maintenance_interval",
            "maintenance_procedure",
            "operation_instruction",
        },
        AnswerIntent.PROCEDURE_STEPS.value: {
            "maintenance_procedure",
            "installation_instruction",
            "operation_instruction",
        },
        AnswerIntent.SAFETY_WARNINGS.value: {"safety_warning"},
        AnswerIntent.TROUBLESHOOTING.value: {"troubleshooting"},
        AnswerIntent.CERTIFICATION_SUMMARY.value: {
            "certification_info",
            "technical_specification",
        },
        AnswerIntent.IDENTIFIER_LOOKUP.value: {
            "spare_parts_table",
            "technical_specification",
            "certification_info",
        },
        AnswerIntent.TABLE_SUMMARY.value: {
            "spare_parts_table",
            "technical_specification",
            "certification_info",
            "drawing_reference",
        },
        AnswerIntent.DOCUMENT_SUMMARY.value: {"overview"},
    }
    _CONTEXTUAL_CHUNK_TYPES = {"overview", "unknown"}
    _CONTEXTUAL_SECTION_TOKENS = {"overview", "summary", "introduction", "general"}

    def assign(
        self,
        *,
        answer_intent_value: str,
        sources: list[PromptSourceView],
        table_source_numbers: set[int],
    ) -> dict[int, str]:
        roles = {
            source.source_number: self._classify(
                answer_intent_value=answer_intent_value,
                source=source,
                table_source_numbers=table_source_numbers,
            )
            for source in sources
        }
        if roles and not any(role == "direct" for role in roles.values()):
            roles[sources[0].source_number] = "direct"
        return roles

    def _classify(
        self,
        *,
        answer_intent_value: str,
        source: PromptSourceView,
        table_source_numbers: set[int],
    ) -> str:
        if self._is_direct(
            answer_intent_value=answer_intent_value,
            source=source,
            table_source_numbers=table_source_numbers,
        ):
            return "direct"
        if self._is_contextual(source):
            return "contextual"
        return "supporting"

    def _is_direct(
        self,
        *,
        answer_intent_value: str,
        source: PromptSourceView,
        table_source_numbers: set[int],
    ) -> bool:
        chunk_type = (source.chunk_type or "").strip().lower()
        if source.source_number in table_source_numbers:
            return answer_intent_value in self._TABLE_DIRECT_INTENTS
        if answer_intent_value == AnswerIntent.IDENTIFIER_LOOKUP.value:
            return bool(source.identifier_values)
        return chunk_type in self._PREFERRED_CHUNK_TYPES.get(answer_intent_value, set())

    def _is_contextual(self, source: PromptSourceView) -> bool:
        chunk_type = (source.chunk_type or "").strip().lower()
        if chunk_type in self._CONTEXTUAL_CHUNK_TYPES:
            return True
        section_path = (source.section_path or "").strip().lower()
        return any(token in section_path for token in self._CONTEXTUAL_SECTION_TOKENS)

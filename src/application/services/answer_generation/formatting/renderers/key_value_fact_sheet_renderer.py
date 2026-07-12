from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.formatting.renderers.support import (
    StructuredContextSourceIndex,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.shared.text.ascii_table_renderer import AsciiTableColumn, render_ascii_table

_SUPPORTED_INTENTS = {
    AnswerIntent.SPECIFICATION_SUMMARY,
    AnswerIntent.CERTIFICATION_SUMMARY,
}
_NARRATIVE_BLOCKERS = ("explain", "why ", "compare", "difference")


class KeyValueFactSheetRenderer:
    def render(
        self,
        *,
        question: str,
        answer_intent: AnswerIntent | None,
        structured_context: StructuredAnswerContext | None,
    ) -> str | None:
        if answer_intent not in _SUPPORTED_INTENTS:
            return None
        if _looks_like_narrative_question(question):
            return None
        if structured_context is None or not structured_context.key_values:
            return None

        source_index = StructuredContextSourceIndex.from_context(structured_context)
        rows = []
        for item in structured_context.key_values:
            rows.append(
                {
                    "label": item.key,
                    "value": _render_value(item.value, item.unit),
                    "pages": source_index.page_label_for_source_number(item.source_number)
                    or "-",
                }
            )
        return render_ascii_table(
            columns=[
                AsciiTableColumn("label", "Field", 30),
                AsciiTableColumn("value", "Value", 38),
                AsciiTableColumn("pages", "Pages", 14),
            ],
            rows=rows,
        )


def _render_value(value: str, unit: str | None) -> str:
    normalized_value = " ".join(str(value or "").split())
    normalized_unit = " ".join(str(unit or "").split())
    if normalized_value and normalized_unit:
        return f"{normalized_value} {normalized_unit}"
    return normalized_value or "-"


def _looks_like_narrative_question(question: str) -> bool:
    normalized = " ".join((question or "").strip().lower().split())
    return any(marker in normalized for marker in _NARRATIVE_BLOCKERS)

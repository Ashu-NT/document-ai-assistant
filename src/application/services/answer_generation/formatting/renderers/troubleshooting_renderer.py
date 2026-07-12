from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.formatting.renderers.support import (
    StructuredContextSourceIndex,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.shared.text.ascii_table_renderer import AsciiTableColumn, render_ascii_table


class TroubleshootingRenderer:
    def render(
        self,
        *,
        answer_intent: AnswerIntent | None,
        structured_context: StructuredAnswerContext | None,
    ) -> str | None:
        if answer_intent != AnswerIntent.TROUBLESHOOTING:
            return None
        if structured_context is None:
            return None

        source_index = StructuredContextSourceIndex.from_context(structured_context)
        rows = []
        for entity in structured_context.entities_of_type("troubleshooting"):
            symptom = _string_or_placeholder(entity.fields.get("symptom"))
            cause = _string_or_placeholder(entity.fields.get("cause"))
            remedy = _string_or_placeholder(entity.fields.get("remedy"))
            if symptom == "-" and cause == "-" and remedy == "-":
                continue
            rows.append(
                {
                    "symptom": symptom,
                    "cause": cause,
                    "remedy": remedy,
                    "pages": source_index.page_label_for_chunk_id(entity.source_chunk_id)
                    or "-",
                }
            )
        if not rows:
            return None

        return render_ascii_table(
            columns=[
                AsciiTableColumn("symptom", "Symptom", 28),
                AsciiTableColumn("cause", "Cause", 28),
                AsciiTableColumn("remedy", "Remedy", 28),
                AsciiTableColumn("pages", "Pages", 14),
            ],
            rows=rows,
        )


def _string_or_placeholder(value: object) -> str:
    text = " ".join(str(value or "").split())
    return text or "-"

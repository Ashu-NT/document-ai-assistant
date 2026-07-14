from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.formatting.renderers.support import (
    StructuredContextSourceIndex,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
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
        rows = self._rows_from_tables(structured_context.tables)
        if not rows:
            rows = self._rows_from_entities(structured_context, source_index)
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

    def _rows_from_entities(
        self,
        structured_context: StructuredAnswerContext,
        source_index: StructuredContextSourceIndex,
    ) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
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
        return rows

    def _rows_from_tables(self, tables: list[AnswerTable]) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        seen: set[tuple[str, str, str, str]] = set()
        for table in tables:
            if table.table_kind != "troubleshooting_table":
                continue
            page_label = _page_label(table.page_start, table.page_end)
            for row in table.rows:
                symptom = _string_or_placeholder(row.cells_by_header.get("Symptom"))
                cause = _string_or_placeholder(row.cells_by_header.get("Cause"))
                remedy = _string_or_placeholder(row.cells_by_header.get("Remedy"))
                key = (symptom, cause, remedy, page_label)
                if key in seen or (symptom == "-" and cause == "-" and remedy == "-"):
                    continue
                seen.add(key)
                rows.append(
                    {
                        "symptom": symptom,
                        "cause": cause,
                        "remedy": remedy,
                        "pages": page_label,
                    }
                )
        return rows


def _string_or_placeholder(value: object) -> str:
    text = " ".join(str(value or "").split())
    return text or "-"


def _page_label(page_start: int | None, page_end: int | None) -> str:
    if page_start is None and page_end is None:
        return "-"
    if page_end is None or page_end == page_start:
        return f"p.{page_start}"
    return f"pp.{page_start}-{page_end}"

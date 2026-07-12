from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.formatting.renderers.support import (
    StructuredContextSourceIndex,
    combine_page_labels,
    format_page_label,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.shared.text.ascii_table_renderer import AsciiTableColumn, render_ascii_table

_SCHEDULE_MARKERS = (
    "maintenance interval",
    "maintenance intervals",
    "service interval",
    "service intervals",
    "schedule",
    "frequency",
    "how often",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "annual",
)
_NARRATIVE_BLOCKERS = ("why ", "explain", "compare", "difference")


class MaintenanceScheduleRenderer:
    def render(
        self,
        *,
        question: str,
        answer_intent: AnswerIntent | None,
        structured_context: StructuredAnswerContext | None,
    ) -> str | None:
        if answer_intent != AnswerIntent.MAINTENANCE_SUMMARY:
            return None
        if not _looks_like_schedule_question(question):
            return None
        entries = list(structured_context.maintenance_entries) if structured_context else []
        if not entries:
            return None

        source_index = StructuredContextSourceIndex.from_context(structured_context)
        rows = []
        notes: list[str] = []
        for entry in entries:
            page_label = combine_page_labels(
                [
                    format_page_label(reference.page_start, reference.page_end)
                    for reference in entry.references
                ]
            ) or source_index.page_label_for_source_number(entry.source_number)
            rows.append(
                {
                    "task": entry.task,
                    "interval": entry.interval,
                    "component": entry.component or "-",
                    "pages": page_label or "-",
                }
            )
            note_text = entry.notes or entry.description
            if note_text:
                notes.append(f"- {entry.task}: {note_text}")

        lines = [
            render_ascii_table(
                columns=[
                    AsciiTableColumn("task", "Task", 30),
                    AsciiTableColumn("interval", "Interval", 32),
                    AsciiTableColumn("component", "Component", 24),
                    AsciiTableColumn("pages", "Pages", 14),
                ],
                rows=rows,
            )
        ]
        if notes:
            lines.extend(["", "Notes:"])
            lines.extend(notes[:6])
        return "\n".join(lines).strip()


def _looks_like_schedule_question(question: str) -> bool:
    normalized = " ".join((question or "").strip().lower().split())
    if not normalized:
        return False
    if any(marker in normalized for marker in _NARRATIVE_BLOCKERS):
        return False
    return any(marker in normalized for marker in _SCHEDULE_MARKERS)

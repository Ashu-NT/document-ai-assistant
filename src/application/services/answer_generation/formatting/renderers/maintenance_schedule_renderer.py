from __future__ import annotations

from src.application.services.answer_generation.intent.answer_intent import AnswerIntent
from src.application.services.answer_generation.formatting.renderers.support import (
    StructuredContextSourceIndex,
    combine_page_labels,
    format_page_label,
)
from src.application.workflows.question_answering.answer_context.maintenance.maintenance_candidate_parser import (
    MaintenanceCandidate,
)
from src.application.workflows.question_answering.answer_context.maintenance.maintenance_table_candidate_extractor import (
    MaintenanceTableCandidateExtractor,
)
from src.application.workflows.question_answering.answer_context.models import (
    StructuredAnswerContext,
)
from src.application.workflows.question_answering.answer_context.tables.answer_table import (
    AnswerTable,
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
    def __init__(
        self,
        maintenance_table_candidate_extractor: (
            MaintenanceTableCandidateExtractor | None
        ) = None,
    ) -> None:
        self.maintenance_table_candidate_extractor = (
            maintenance_table_candidate_extractor
            or MaintenanceTableCandidateExtractor()
        )

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
        source_index = StructuredContextSourceIndex.from_context(structured_context)
        if entries:
            rows, notes = self._rows_from_entries(entries, source_index)
        elif structured_context is not None:
            rows, notes = self._rows_from_tables(structured_context.tables)
        else:
            rows, notes = ([], [])
        if not rows:
            return None

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

    @staticmethod
    def _rows_from_entries(
        entries,
        source_index: StructuredContextSourceIndex,
    ) -> tuple[list[dict[str, str]], list[str]]:
        rows: list[dict[str, str]] = []
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
        return rows, notes

    def _rows_from_tables(
        self,
        tables: list[AnswerTable],
    ) -> tuple[list[dict[str, str]], list[str]]:
        rows: list[dict[str, str]] = []
        notes: list[str] = []
        seen: set[tuple[str, str, str, str]] = set()
        for table in tables:
            page_label = format_page_label(table.page_start, table.page_end) or "-"
            for candidate in self.maintenance_table_candidate_extractor.extract(table):
                row, note = self._row_from_candidate(
                    candidate,
                    page_label=page_label,
                )
                key = (
                    row["task"].casefold(),
                    row["interval"].casefold(),
                    row["component"].casefold(),
                    row["pages"],
                )
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
                if note:
                    notes.append(note)
        return rows, notes

    @staticmethod
    def _row_from_candidate(
        candidate: MaintenanceCandidate,
        *,
        page_label: str,
    ) -> tuple[dict[str, str], str | None]:
        row = {
            "task": candidate.task,
            "interval": candidate.interval or "Not specified",
            "component": candidate.component or "-",
            "pages": page_label or "-",
        }
        note_text = candidate.notes or candidate.description
        note = f"- {candidate.task}: {note_text}" if note_text else None
        return row, note


def _looks_like_schedule_question(question: str) -> bool:
    normalized = " ".join((question or "").strip().lower().split())
    if not normalized:
        return False
    if any(marker in normalized for marker in _NARRATIVE_BLOCKERS):
        return False
    return any(marker in normalized for marker in _SCHEDULE_MARKERS)

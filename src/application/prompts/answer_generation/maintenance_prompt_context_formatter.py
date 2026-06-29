from __future__ import annotations

from collections import OrderedDict
from collections.abc import Sequence

from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerMaintenanceEntry,
    AnswerMaintenanceReference,
)

_NOT_SPECIFIED = "Not specified"


class MaintenancePromptContextFormatter:
    def format(
        self,
        entries: Sequence[AnswerMaintenanceEntry],
    ) -> list[str]:
        lines = ["Maintenance entries:"]
        total_entries = len(entries)
        for index, entry in enumerate(entries, start=1):
            lines.extend(self._format_entry(index, entry))
            if index < total_entries:
                lines.append("--------------------------------------------------")
        return lines

    def _format_entry(
        self,
        index: int,
        entry: AnswerMaintenanceEntry,
    ) -> list[str]:
        lines = [f"{index}. {entry.task}", "   Description"]
        lines.append(f"   {self._description(entry)}")
        lines.extend(
            [
                "",
                "   Interval / Frequency",
                f"   {entry.interval or _NOT_SPECIFIED}",
                "",
                "   Component",
                f"   {entry.component or _NOT_SPECIFIED}",
                "",
                "   Reference",
            ]
        )
        lines.extend(self._reference_lines(entry))
        return lines

    def _description(self, entry: AnswerMaintenanceEntry) -> str:
        return entry.description or entry.notes or entry.task

    def _reference_lines(self, entry: AnswerMaintenanceEntry) -> list[str]:
        references = entry.references or [
            AnswerMaintenanceReference(
                source_number=entry.source_number,
                page_start=entry.page_start,
                page_end=entry.page_end,
                section_path=entry.section_path,
            )
        ]
        page_lines = self._page_lines(references)
        section_lines = self._section_lines(entry, references)
        source_numbers = entry.source_numbers or [reference.source_number for reference in references]

        lines: list[str] = []
        if page_lines:
            lines.extend(page_lines)
        if section_lines:
            lines.extend(section_lines)
        if source_numbers:
            rendered_sources = ", ".join(
                f"SOURCE {source_number}" for source_number in source_numbers
            )
            lines.append(f"   Sources: {rendered_sources}")
        if not lines:
            return [f"   {_NOT_SPECIFIED}"]
        return lines

    def _page_lines(
        self,
        references: Sequence[AnswerMaintenanceReference],
    ) -> list[str]:
        page_ranges = self._unique_page_ranges(references)
        if not page_ranges:
            return []
        if len(page_ranges) == 1:
            label = "Page" if "-" not in page_ranges[0] else "Pages"
            return [f"   {label} {page_ranges[0]}"]
        return [f"   Pages {', '.join(page_ranges)}"]

    def _section_lines(
        self,
        entry: AnswerMaintenanceEntry,
        references: Sequence[AnswerMaintenanceReference],
    ) -> list[str]:
        section_paths = entry.section_paths or [
            reference.section_path for reference in references if reference.section_path
        ]
        ordered_sections: OrderedDict[str, None] = OrderedDict()
        for section_path in section_paths:
            if section_path:
                ordered_sections.setdefault(section_path, None)
        rendered_sections = list(ordered_sections.keys())
        if not rendered_sections:
            return []
        if len(rendered_sections) == 1:
            return [f"   Section: {rendered_sections[0]}"]
        lines = ["   Sections:"]
        lines.extend(f"   - {section}" for section in rendered_sections)
        return lines

    @staticmethod
    def _unique_page_ranges(
        references: Sequence[AnswerMaintenanceReference],
    ) -> list[str]:
        ordered: OrderedDict[str, None] = OrderedDict()
        for reference in references:
            page_range = MaintenancePromptContextFormatter._format_page_range(
                reference.page_start,
                reference.page_end,
            )
            if page_range is not None:
                ordered.setdefault(page_range, None)
        return list(ordered.keys())

    @staticmethod
    def _format_page_range(
        page_start: int | None,
        page_end: int | None,
    ) -> str | None:
        if page_start is None and page_end is None:
            return None
        if page_start == page_end:
            return str(page_start)
        if page_start is None:
            return str(page_end)
        if page_end is None:
            return str(page_start)
        return f"{page_start}-{page_end}"

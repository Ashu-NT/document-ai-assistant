from __future__ import annotations

from typing import Sequence

from src.application.services.answer_generation.formatting.spare_parts.spare_parts_group import (
    SparePartsGroup,
)
from src.application.services.answer_generation.formatting.spare_parts.spare_parts_row_presentation import (
    row_field_label,
    visible_row_fields,
)


class SparePartsSummaryRenderer:
    def render(self, groups: Sequence[SparePartsGroup]) -> str:
        lines = [
            "Multiple spare-parts tables were found in the retrieved evidence.",
            "Relevant sections:",
            "",
        ]
        for index, group in enumerate(groups, start=1):
            fields = visible_row_fields(group.rows)
            field_labels = ", ".join(row_field_label(field) for field in fields[:4]) or "-"
            lines.append(f"{index}. {group.section_title}")
            lines.append(f"   Pages: {self._page_range(group.page_start, group.page_end)}")
            lines.append(f"   Section: {group.section_path or '-'}")
            lines.append(f"   Parsed rows: {len(group.rows)}")
            lines.append(f"   Available fields: {field_labels}")
            lines.append("")
        lines.append(
            "Ask for a specific component, assembly, or section to expand one table in detail."
        )
        return "\n".join(lines).strip()

    @staticmethod
    def _page_range(page_start: int | None, page_end: int | None) -> str:
        if page_start is None and page_end is None:
            return "-"
        if page_end is None or page_end == page_start:
            return str(page_start)
        return f"{page_start}-{page_end}"

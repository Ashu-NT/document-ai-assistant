from __future__ import annotations

from collections import OrderedDict
from typing import Sequence

from src.application.workflows.question_answering.answer_context.structured_answer_context import (
    AnswerSectionGroup,
    AnswerSource,
)


class SectionGroupBuilder:
    def build(self, sources: Sequence[AnswerSource]) -> list[AnswerSectionGroup]:
        grouped: OrderedDict[str, AnswerSectionGroup] = OrderedDict()
        for source in sources:
            key = source.section_path or "Unscoped evidence"
            if key not in grouped:
                grouped[key] = AnswerSectionGroup(
                    group_name=self._section_group_name(source.section_path),
                    section_path=source.section_path,
                    page_start=source.page_start,
                    page_end=source.page_end,
                )
            group = grouped[key]
            group.source_numbers.append(source.source_number)
            group.page_start = self._min_page(group.page_start, source.page_start)
            group.page_end = self._max_page(group.page_end, source.page_end)
        return list(grouped.values())

    @staticmethod
    def _section_group_name(section_path: str | None) -> str:
        if not section_path:
            return "Unscoped evidence"
        return section_path.split(" > ")[-1]

    @staticmethod
    def _min_page(current: int | None, candidate: int | None) -> int | None:
        if current is None:
            return candidate
        if candidate is None:
            return current
        return min(current, candidate)

    @staticmethod
    def _max_page(current: int | None, candidate: int | None) -> int | None:
        if current is None:
            return candidate
        if candidate is None:
            return current
        return max(current, candidate)

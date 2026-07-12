from __future__ import annotations

from dataclasses import dataclass

from src.application.services.answer_generation.formatting.renderers.support.source_reference_formatter import (
    combine_page_labels,
    format_page_label,
    simplify_section_path,
)
from src.application.workflows.question_answering.answer_context.models import (
    AnswerSource,
    StructuredAnswerContext,
)


@dataclass(slots=True)
class StructuredContextSourceIndex:
    source_by_chunk_id: dict[str, AnswerSource]
    source_by_number: dict[int, AnswerSource]

    @classmethod
    def from_context(
        cls,
        context: StructuredAnswerContext | None,
    ) -> "StructuredContextSourceIndex":
        sources = list(context.sources) if context is not None else []
        return cls(
            source_by_chunk_id={source.chunk_id: source for source in sources if source.chunk_id},
            source_by_number={source.source_number: source for source in sources},
        )

    def page_label_for_chunk_id(self, chunk_id: str | None) -> str | None:
        if not chunk_id:
            return None
        source = self.source_by_chunk_id.get(chunk_id)
        if source is None:
            return None
        return format_page_label(source.page_start, source.page_end)

    def page_label_for_source_number(self, source_number: int | None) -> str | None:
        if source_number is None:
            return None
        source = self.source_by_number.get(source_number)
        if source is None:
            return None
        return format_page_label(source.page_start, source.page_end)

    def combined_page_labels_for_chunk_ids(self, chunk_ids: list[str]) -> str | None:
        return combine_page_labels(
            self.page_label_for_chunk_id(chunk_id) for chunk_id in chunk_ids
        )

    def section_label_for_chunk_id(self, chunk_id: str | None) -> str | None:
        if not chunk_id:
            return None
        source = self.source_by_chunk_id.get(chunk_id)
        if source is None:
            return None
        return simplify_section_path(source.section_path)

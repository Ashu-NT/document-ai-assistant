from __future__ import annotations

from collections import OrderedDict

from src.application.prompts.answer_generation.prompt_context.models.prompt_source_family_view import (
    PromptSourceFamilyView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)


class PromptSourceFamilyBuilder:
    def build(
        self,
        *,
        sources: list[PromptSourceView],
        roles_by_source_number: dict[int, str],
        table_source_numbers: set[int],
    ) -> list[PromptSourceFamilyView]:
        grouped: OrderedDict[str, list[PromptSourceView]] = OrderedDict()
        for source in sources:
            grouped.setdefault(self._family_key(source), []).append(source)
        return [
            self._build_family(
                family_id=family_id,
                sources=family_sources,
                roles_by_source_number=roles_by_source_number,
                table_source_numbers=table_source_numbers,
            )
            for family_id, family_sources in grouped.items()
        ]

    def _build_family(
        self,
        *,
        family_id: str,
        sources: list[PromptSourceView],
        roles_by_source_number: dict[int, str],
        table_source_numbers: set[int],
    ) -> PromptSourceFamilyView:
        direct_source_numbers = self._numbers_for_role(
            sources, roles_by_source_number, "direct"
        )
        supporting_source_numbers = self._numbers_for_role(
            sources,
            roles_by_source_number,
            "supporting",
        )
        contextual_source_numbers = self._numbers_for_role(
            sources,
            roles_by_source_number,
            "contextual",
        )
        anchor_source_number = (
            direct_source_numbers[0] if direct_source_numbers else sources[0].source_number
        )
        anchor_source = next(
            source
            for source in sources
            if source.source_number == anchor_source_number
        )
        return PromptSourceFamilyView(
            family_id=family_id,
            family_label=self._family_label(anchor_source),
            anchor_source_number=anchor_source_number,
            anchor_chunk_type=anchor_source.chunk_type,
            section_path=anchor_source.section_path,
            page_start=self._min_page(sources),
            page_end=self._max_page(sources),
            direct_source_numbers=direct_source_numbers,
            supporting_source_numbers=supporting_source_numbers,
            contextual_source_numbers=contextual_source_numbers,
            table_source_numbers=sorted(
                source.source_number
                for source in sources
                if source.source_number in table_source_numbers
            ),
        )

    @staticmethod
    def _family_key(source: PromptSourceView) -> str:
        if source.section_id:
            return f"section:{source.section_id}"
        if source.section_path:
            return f"path:{source.section_path.lower()}"
        return f"chunk:{source.chunk_id}"

    @staticmethod
    def _family_label(source: PromptSourceView) -> str:
        if source.section_path:
            return source.section_path.split(" > ")[-1]
        if source.chunk_name:
            return source.chunk_name
        return source.chunk_type or source.chunk_id

    @staticmethod
    def _numbers_for_role(
        sources: list[PromptSourceView],
        roles_by_source_number: dict[int, str],
        role: str,
    ) -> list[int]:
        return [
            source.source_number
            for source in sources
            if roles_by_source_number.get(source.source_number) == role
        ]

    @staticmethod
    def _min_page(sources: list[PromptSourceView]) -> int | None:
        pages = [source.page_start for source in sources if source.page_start is not None]
        return min(pages) if pages else None

    @staticmethod
    def _max_page(sources: list[PromptSourceView]) -> int | None:
        pages = [source.page_end for source in sources if source.page_end is not None]
        return max(pages) if pages else None

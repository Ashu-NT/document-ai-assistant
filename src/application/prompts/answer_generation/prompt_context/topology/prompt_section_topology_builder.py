from __future__ import annotations

from collections import OrderedDict

from src.application.prompts.answer_generation.prompt_context.models.prompt_section_topology_view import (
    PromptSectionTopologyView,
)
from src.application.prompts.answer_generation.prompt_context.models.prompt_source_view import (
    PromptSourceView,
)


class PromptSectionTopologyBuilder:
    def build(
        self,
        *,
        sources: list[PromptSourceView],
        roles_by_source_number: dict[int, str],
        table_source_numbers: set[int],
    ) -> list[PromptSectionTopologyView]:
        grouped: OrderedDict[str, list[PromptSourceView]] = OrderedDict()
        for source in sources:
            section_key = source.section_path or "Unscoped evidence"
            grouped.setdefault(section_key, []).append(source)
        return [
            self._build_section(
                section_key=section_key,
                sources=section_sources,
                roles_by_source_number=roles_by_source_number,
                table_source_numbers=table_source_numbers,
            )
            for section_key, section_sources in grouped.items()
        ]

    def _build_section(
        self,
        *,
        section_key: str,
        sources: list[PromptSourceView],
        roles_by_source_number: dict[int, str],
        table_source_numbers: set[int],
    ) -> PromptSectionTopologyView:
        section_path = sources[0].section_path or "Unscoped evidence"
        return PromptSectionTopologyView(
            section_key=section_key,
            section_name=section_path.split(" > ")[-1],
            section_path=section_path,
            parent_section_path=self._parent_section_path(section_path),
            page_start=self._min_page(sources),
            page_end=self._max_page(sources),
            source_numbers=[source.source_number for source in sources],
            direct_source_numbers=self._numbers_for_role(
                sources, roles_by_source_number, "direct"
            ),
            supporting_source_numbers=self._numbers_for_role(
                sources,
                roles_by_source_number,
                "supporting",
            ),
            contextual_source_numbers=self._numbers_for_role(
                sources,
                roles_by_source_number,
                "contextual",
            ),
            table_source_numbers=sorted(
                source.source_number
                for source in sources
                if source.source_number in table_source_numbers
            ),
        )

    @staticmethod
    def _parent_section_path(section_path: str) -> str | None:
        if " > " not in section_path:
            return None
        return section_path.rsplit(" > ", maxsplit=1)[0]

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

from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.parsing.builders.chunking.builders.fragment.table_fragment_builder import (
    TableFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    resolve_parser_extra,
)
from src.application.workflows.parsing.parsing_value_coercion import (
    coerce_float,
    coerce_positive_int,
)
from src.application.workflows.parsing.tables.families import (
    LogicalTableFamilyRowMerger,
)
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


@dataclass(slots=True)
class TableFamilyFragmentBuildResult:
    fragments: list[ChunkFragment]
    consumed_element_ids: set[str]


class LogicalTableFamilyFragmentBuilder:
    def __init__(
        self,
        *,
        table_fragment_builder: TableFragmentBuilder,
        row_merger: LogicalTableFamilyRowMerger | None = None,
    ) -> None:
        self.table_fragment_builder = table_fragment_builder
        self.row_merger = row_merger or LogicalTableFamilyRowMerger()

    def build(
        self,
        *,
        section: DocumentSection,
        elements: list[CanonicalElement],
        excluded_element_ids: set[str] | None = None,
    ) -> TableFamilyFragmentBuildResult:
        family_buckets = self._collect_family_buckets(
            elements,
            excluded_element_ids=excluded_element_ids or set(),
        )
        fragments: list[ChunkFragment] = []
        consumed_element_ids: set[str] = set()

        for family_elements in family_buckets.values():
            fragment = self._build_family_fragment(
                section=section,
                elements=elements,
                family_elements=family_elements,
            )
            if fragment is None:
                continue
            fragments.append(fragment)
            consumed_element_ids.update(
                element.element_id for element in family_elements if element.element_id
            )

        return TableFamilyFragmentBuildResult(
            fragments=fragments,
            consumed_element_ids=consumed_element_ids,
        )

    @staticmethod
    def _collect_family_buckets(
        elements: list[CanonicalElement],
        *,
        excluded_element_ids: set[str],
    ) -> dict[str, list[CanonicalElement]]:
        buckets: dict[str, list[CanonicalElement]] = {}
        for element in elements:
            if element.element_id in excluded_element_ids:
                continue
            family_id = str(
                resolve_parser_extra(element).get("logical_table_family_id") or ""
            ).strip()
            if family_id:
                buckets.setdefault(family_id, []).append(element)
        return {
            family_id: sorted(
                family_elements,
                key=lambda element: (
                    coerce_positive_int(resolve_parser_extra(element).get("family_index"))
                    or 10_000,
                    element.reading_order or 0,
                    element.element_id,
                ),
            )
            for family_id, family_elements in buckets.items()
        }

    def _build_family_fragment(
        self,
        *,
        section: DocumentSection,
        elements: list[CanonicalElement],
        family_elements: list[CanonicalElement],
    ) -> ChunkFragment | None:
        lead_element = family_elements[0]
        lead_index = elements.index(lead_element)
        context_text = self.table_fragment_builder.table_context_text(
            elements=elements,
            index=lead_index,
            element=lead_element,
        )
        markdown_parts = [
            self.table_fragment_builder.table_markdown_text(element)
            for element in family_elements
        ]
        markdown_text = "\n\n".join(part for part in markdown_parts if part)
        text = self.table_fragment_builder.compose_table_text(
            context_text=context_text,
            markdown_text=markdown_text,
        )
        if not text:
            return None

        parser_extra = resolve_parser_extra(lead_element)
        merged_rows = self.row_merger.merge_row_groups(
            [
                self.table_fragment_builder.table_rows(element) or []
                for element in family_elements
            ]
        )
        body_row_count = max(0, len(merged_rows or []) - 1)
        merged_structure_metadata = self.table_fragment_builder.merge_family_table_metadata(
            family_elements
        )

        return ChunkFragment(
            text=text,
            chunk_type=self.table_fragment_builder.table_chunk_type(lead_element, text),
            standalone=True,
            order_index=lead_element.reading_order or lead_index,
            section_id=section.section_id,
            section_title=section.title,
            section_path=list(section.section_path),
            section_level=section.level,
            parent_section_id=section.parent_section_id,
            element_ids=[element.element_id for element in family_elements],
            table_ids=[
                element.table_id
                for element in family_elements
                if element.table_id is not None
            ],
            page_start=min(
                (
                    element.source.page_start
                    for element in family_elements
                    if element.source.page_start is not None
                ),
                default=None,
            ),
            page_end=max(
                (
                    element.source.page_end
                    for element in family_elements
                    if element.source.page_end is not None
                ),
                default=None,
            ),
            token_count=self.table_fragment_builder.text_splitter.count_tokens(text),
            table_context=context_text,
            table_rows=merged_rows,
            logical_table_family_id=str(
                parser_extra.get("logical_table_family_id") or ""
            ).strip()
            or None,
            logical_table_family_index=1,
            logical_table_family_total=1,
            logical_table_continuation_role="single",
            table_category=str(parser_extra.get("table_category") or "").strip() or None,
            table_category_confidence=coerce_float(
                parser_extra.get("table_category_confidence")
            ),
            table_row_start=1 if body_row_count > 0 else None,
            table_row_end=body_row_count if body_row_count > 0 else None,
            table_shape=merged_structure_metadata["table_shape"],
            table_structure_quality=merged_structure_metadata["table_structure_quality"],
            header_paths=merged_structure_metadata["header_paths"],
            axis_summary=merged_structure_metadata["axis_summary"],
        )

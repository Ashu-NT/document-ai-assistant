from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.picture_fragment_builder import (
    PictureFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.logical_table_family_fragment_builder import (
    LogicalTableFamilyFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.table_fragment_builder import (
    TableFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.builders.structured_section_fragment_builder import (
    StructuredSectionFragmentBuilder,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    is_furniture_or_embedded_picture,
    is_low_value_fragment,
    resolve_parser_extra,
)
from src.application.workflows.parsing.parsing_value_coercion import coerce_float
from src.application.workflows.parsing.tables.families import (
    LogicalTableFamilyRowMerger,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.table_chunk_eligibility_policy import (
    TableChunkEligibilityPolicy,
)
from src.domain.common import ChunkType, ElementType
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class ChunkFragmentBuilder:
 
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        structured_fragment_builder: StructuredSectionFragmentBuilder | None = None,
        include_picture_chunks: bool = True,
        include_table_context: bool = True,
        asset_context_window: int = 1,
        asset_context_max_tokens: int = 72,
        page_sizes: dict[int, tuple[float, float]] | None = None,
    ) -> None:
        self.text_splitter = text_splitter
        self.include_picture_chunks = include_picture_chunks

        self.table_chunk_eligibility_policy = (
            TableChunkEligibilityPolicy(
                text_splitter=text_splitter,
            )
        )

        self.asset_context_resolver = AssetContextResolver(
            text_splitter=text_splitter,
            asset_context_window=max(
                0,
                asset_context_window,
            ),
            asset_context_max_tokens=max(
                12,
                asset_context_max_tokens,
            ),
            element_contributes_to_chunk=(
                self._element_contributes_to_chunk
            ),
        )

        self.structured_fragment_builder = (
            structured_fragment_builder
            or StructuredSectionFragmentBuilder(
                text_splitter=text_splitter,
                table_chunk_eligibility_policy=(
                    self.table_chunk_eligibility_policy
                ),
            )
        )

        self.table_fragment_builder = TableFragmentBuilder(
            text_splitter=text_splitter,
            include_table_context=include_table_context,
            asset_context_resolver=self.asset_context_resolver,
            table_chunk_eligibility_policy=(
                self.table_chunk_eligibility_policy
            ),
        )

        self.logical_table_family_fragment_builder = (
            LogicalTableFamilyFragmentBuilder(
                table_fragment_builder=self.table_fragment_builder,
            )
        )

        self.logical_table_family_row_merger = (
            LogicalTableFamilyRowMerger()
        )

        self.picture_fragment_builder = PictureFragmentBuilder(
            page_sizes=page_sizes or {},
            asset_context_resolver=self.asset_context_resolver,
        )
 
    def build_section_fragments(
        self,
        *,
        document_title: str | None,
        document_type: DocumentType | None,
        section: DocumentSection,
        elements: list[CanonicalElement],
        document_sections_combined_text: str = "",
    ) -> list[ChunkFragment]:
        structured_fragments, consumed_element_ids = (
            self.structured_fragment_builder.build(
                document_title=document_title,
                document_type=document_type,
                section=section,
                elements=elements,
                document_sections_combined_text=document_sections_combined_text,
            )
        )
        fragments: list[ChunkFragment] = list(structured_fragments)
        self._enrich_structured_table_fragments(
            fragments=fragments,
            elements=elements,
        )
        family_result = self.logical_table_family_fragment_builder.build(
            section=section,
            elements=elements,
            excluded_element_ids=consumed_element_ids,
        )
        fragments.extend(family_result.fragments)
        consumed_element_ids.update(family_result.consumed_element_ids)

        list_run_id_by_element_id = self._assign_list_run_ids(section, elements)

        for index, element in enumerate(elements):
            if element.element_id in consumed_element_ids:
                continue
            fragment = self._build_fragment_from_element(
                section,
                elements,
                index,
                element,
            )
            if fragment is not None:
                fragment.list_run_id = list_run_id_by_element_id.get(element.element_id)
                fragments.append(fragment)

        self._apply_list_run_totals(fragments)

        return sorted(fragments, key=lambda fragment: fragment.order_index)

    @staticmethod
    def _assign_list_run_ids(
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> dict[str, str]:
        """Groups contiguous LIST_ITEM elements (in reading order) into
        numbered runs, e.g. the steps of one maintenance procedure."""
        list_run_id_by_element_id: dict[str, str] = {}
        run_index = 0
        in_run = False

        for element in elements:
            if element.element_type == ElementType.LIST_ITEM:
                if not in_run:
                    run_index += 1
                    in_run = True
                list_run_id_by_element_id[element.element_id] = (
                    f"{section.section_id}::list_run_{run_index}"
                )
            else:
                in_run = False

        return list_run_id_by_element_id

    @staticmethod
    def _apply_list_run_totals(fragments: list[ChunkFragment]) -> None:
        totals: dict[str, int] = {}
        for fragment in fragments:
            if fragment.list_run_id is None:
                continue
            totals[fragment.list_run_id] = (
                totals.get(fragment.list_run_id, 0) + fragment.token_count
            )

        for fragment in fragments:
            if fragment.list_run_id is not None:
                fragment.list_run_total_tokens = totals[fragment.list_run_id]

    def _build_fragment_from_element(
        self,
        section: DocumentSection,
        elements: list[CanonicalElement],
        index: int,
        element: CanonicalElement,
    ) -> ChunkFragment | None:
        if self._is_document_index_element(element):
            return None

        table_rows: list[list[str]] | None = None
        table_context: str | None = None
        table_metadata: dict[str, object] = {}
        if element.table_id is not None or element.element_type == ElementType.TABLE:
            if not self.table_fragment_builder.should_chunk_table_element(element):
                return None
            table_context = self.table_fragment_builder.table_context_text(
                elements=elements, index=index, element=element
            )
            markdown_text = self.table_fragment_builder.table_markdown_text(element)
            text = self.table_fragment_builder.compose_table_text(
                context_text=table_context,
                markdown_text=markdown_text,
            )
            chunk_type = self.table_fragment_builder.table_chunk_type(element, text)
            standalone = True
            table_rows = self.table_fragment_builder.table_rows(element)
            table_metadata = self.table_fragment_builder.table_metadata(element)
        elif element.picture_id is not None or element.element_type == ElementType.PICTURE:
            if not self.include_picture_chunks and not self.picture_fragment_builder.is_large_picture(
                element
            ):
                return None
            text = self.picture_fragment_builder.picture_fragment_text(
                elements=elements,
                index=index,
                element=element,
            )
            if not text:
                return None
            chunk_type = self.picture_fragment_builder.picture_chunk_type(text)
            standalone = True
        elif element.form_id is not None or element.element_type == ElementType.FORM:
            if not self._element_contributes_to_chunk(element):
                return None
            text = self._form_fragment_text(resolve_parser_extra(element))
            if not text:
                return None
            chunk_type = ChunkType.FORM_DATA
            standalone = True
        elif element.element_type == ElementType.FORMULA:
            if not self._element_contributes_to_chunk(element):
                return None
            text = clean_chunk_text(element.text)
            chunk_type = ChunkType.FORMULA
            standalone = True
        elif element.element_type == ElementType.CODE:
            if not self._element_contributes_to_chunk(element):
                return None
            text = clean_chunk_text(element.text)
            chunk_type = ChunkType.CODE_BLOCK
            standalone = True
        else:
            if not self._element_contributes_to_chunk(element):
                return None
            text = clean_chunk_text(element.text)
            chunk_type = ChunkType.GENERAL
            standalone = False

        if not text or is_low_value_fragment(text):
            return None

        return ChunkFragment(
            text=text,
            chunk_type=chunk_type,
            standalone=standalone,
            order_index=element.reading_order or index,
            section_id=section.section_id,
            section_title=section.title,
            section_path=list(section.section_path),
            section_level=section.level,
            parent_section_id=section.parent_section_id,
            element_ids=[element.element_id],
            table_ids=[element.table_id] if element.table_id is not None else [],
            picture_ids=[element.picture_id] if element.picture_id is not None else [],
            form_ids=[element.form_id] if element.form_id is not None else [],
            page_start=element.source.page_start,
            page_end=element.source.page_end,
            token_count=self.text_splitter.count_tokens(text),
            table_context=table_context,
            table_rows=table_rows,
            logical_table_family_id=table_metadata.get("logical_table_family_id"),
            logical_table_family_index=table_metadata.get("logical_table_family_index"),
            logical_table_family_total=table_metadata.get("logical_table_family_total"),
            logical_table_continuation_role=table_metadata.get(
                "logical_table_continuation_role"
            ),
            table_category=table_metadata.get("table_category"),
            table_category_confidence=table_metadata.get("table_category_confidence"),
            table_row_start=1 if table_rows and len(table_rows) > 1 else None,
            table_row_end=(len(table_rows) - 1) if table_rows and len(table_rows) > 1 else None,
            table_shape=table_metadata.get("table_shape"),
            table_structure_quality=table_metadata.get("table_structure_quality"),
            header_paths=table_metadata.get("header_paths") or [],
            axis_summary=table_metadata.get("axis_summary") or {},
        )

    @staticmethod
    def _form_fragment_text(parser_extra: dict) -> str | None:
        parts: list[str] = []

        caption = clean_chunk_text(parser_extra.get("caption"))
        if caption:
            parts.append(f"Form: {caption}")

        nearby_text = clean_chunk_text(parser_extra.get("nearby_text"))
        if nearby_text:
            parts.append(f"Context: {nearby_text}")

        fields = parser_extra.get("form_fields")
        if isinstance(fields, list):
            for entry in fields:
                if not isinstance(entry, dict):
                    continue
                key_text = clean_chunk_text(entry.get("key_text"))
                value_text = clean_chunk_text(entry.get("value_text"))
                if key_text and value_text:
                    parts.append(f"{key_text}: {value_text}")
                elif key_text:
                    parts.append(key_text)
                elif value_text:
                    parts.append(value_text)

        return "\n".join(parts).strip() or None

    @staticmethod
    def _element_contributes_to_chunk(element: CanonicalElement) -> bool:
        parser_extra = resolve_parser_extra(element)
        if element.element_type == ElementType.SECTION_HEADER:
            return parser_extra.get("structural_heading") is False
        if element.element_type in {
            ElementType.PICTURE,
            ElementType.TITLE,
            ElementType.CAPTION,
        }:
            return False

        return not is_furniture_or_embedded_picture(element)

    def _is_document_index_element(self, element: CanonicalElement) -> bool:
        parser_extra = resolve_parser_extra(element)
        item_label = str(parser_extra.get("item_label") or "").strip().lower()
        raw_source_type = str(parser_extra.get("raw_source_type") or "").strip().lower()
        return item_label == "document_index" or raw_source_type == "documentindex"

    def _enrich_structured_table_fragments(
        self,
        *,
        fragments: list[ChunkFragment],
        elements: list[CanonicalElement],
    ) -> None:
        element_by_id = {element.element_id: element for element in elements}

        for fragment in fragments:
            family_id = self._resolve_fragment_family_id(
                fragment=fragment,
                element_by_id=element_by_id,
            )
            if family_id is None:
                continue

            family_elements = [
                element
                for element in elements
                if (
                    str(
                        resolve_parser_extra(element).get(
                            "logical_table_family_id"
                        )
                        or ""
                    ).strip()
                    == family_id
                    and self.table_fragment_builder.should_chunk_table_element(
                        element
                    )
                )
            ]
            if not family_elements:
                continue

            first_element = family_elements[0]
            parser_extra = resolve_parser_extra(first_element)
            merged_rows = self.logical_table_family_row_merger.merge_row_groups(
                [
                    self.table_fragment_builder.table_rows(element) or []
                    for element in family_elements
                ]
            )
            merged_structure_metadata = (
                self.table_fragment_builder.merge_family_table_metadata(family_elements)
            )
            fragment.logical_table_family_id = family_id
            fragment.logical_table_family_index = 1
            fragment.logical_table_family_total = 1
            fragment.logical_table_continuation_role = "single"
            fragment.table_ids = [
                element.table_id
                for element in family_elements
                if element.table_id is not None
            ]
            fragment.table_category = (
                str(parser_extra.get("table_category") or "").strip() or None
            )
            fragment.table_category_confidence = coerce_float(
                parser_extra.get("table_category_confidence")
            )
            fragment.table_shape = merged_structure_metadata["table_shape"]
            fragment.table_structure_quality = merged_structure_metadata[
                "table_structure_quality"
            ]
            fragment.header_paths = merged_structure_metadata["header_paths"]
            fragment.axis_summary = merged_structure_metadata["axis_summary"]
            if merged_rows:
                fragment.table_rows = merged_rows
                fragment.table_row_start = 1
                fragment.table_row_end = len(merged_rows) - 1 if len(merged_rows) > 1 else None

    @staticmethod
    def _resolve_fragment_family_id(
        *,
        fragment: ChunkFragment,
        element_by_id: dict[str, CanonicalElement],
    ) -> str | None:
        for element_id in fragment.element_ids:
            element = element_by_id.get(element_id)
            if element is None:
                continue
            family_id = str(
                resolve_parser_extra(element).get("logical_table_family_id") or ""
            ).strip()
            if family_id:
                return family_id
        return None

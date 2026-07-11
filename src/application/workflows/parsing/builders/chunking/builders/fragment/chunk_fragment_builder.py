from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.builders.fragment.picture_fragment_builder import (
    PictureFragmentBuilder,
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
        self.structured_fragment_builder = (
            structured_fragment_builder
            or StructuredSectionFragmentBuilder(
                text_splitter=text_splitter,
            )
        )
        self.asset_context_resolver = AssetContextResolver(
            text_splitter=text_splitter,
            asset_context_window=max(0, asset_context_window),
            asset_context_max_tokens=max(12, asset_context_max_tokens),
            element_contributes_to_chunk=self._element_contributes_to_chunk,
        )
        self.table_fragment_builder = TableFragmentBuilder(
            text_splitter=text_splitter,
            include_table_context=include_table_context,
            asset_context_resolver=self.asset_context_resolver,
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
                fragments.append(fragment)

        return sorted(fragments, key=lambda fragment: fragment.order_index)

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
        if element.table_id is not None or element.element_type == ElementType.TABLE:
            if not self.table_fragment_builder.should_chunk_table_element(element):
                return None
            text = self.table_fragment_builder.table_fragment_text(
                elements=elements, index=index, element=element
            )
            chunk_type = self.table_fragment_builder.table_chunk_type(element, text)
            standalone = True
            table_rows = resolve_parser_extra(element).get("table_rows") or None
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
            page_start=element.source.page_start,
            page_end=element.source.page_end,
            token_count=self.text_splitter.count_tokens(text),
            table_rows=table_rows,
        )

    @staticmethod
    def _element_contributes_to_chunk(element: CanonicalElement) -> bool:
        if element.element_type in {
            ElementType.SECTION_HEADER,
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

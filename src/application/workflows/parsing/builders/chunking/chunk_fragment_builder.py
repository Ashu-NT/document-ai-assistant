from src.application.workflows.parsing.builders.chunking.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.chunking_utils import (
    clean_chunk_text,
    is_low_value_fragment,
)
from src.domain.common import ChunkType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class ChunkFragmentBuilder:
    def __init__(self, *, text_splitter: ChunkTextSplitter) -> None:
        self.text_splitter = text_splitter

    def build_section_fragments(
        self,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> list[ChunkFragment]:
        fragments: list[ChunkFragment] = []

        for element in elements:
            fragment = self._build_fragment_from_element(section, element)
            if fragment is not None:
                fragments.append(fragment)

        return fragments

    def _build_fragment_from_element(
        self,
        section: DocumentSection,
        element: CanonicalElement,
    ) -> ChunkFragment | None:
        if self._is_document_index_element(element):
            return None

        if element.table_id is not None or element.element_type == ElementType.TABLE:
            if not self._should_chunk_table_element(element):
                return None
            text = self._table_fragment_text(element)
            chunk_type = self._table_chunk_type(element, text)
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

        parser_extra = (
            element.parser_metadata.extra
            if element.parser_metadata is not None
            and element.parser_metadata.extra is not None
            else {}
        )
        parent_ref = parser_extra.get("parent_ref")
        if isinstance(parent_ref, str) and parent_ref.startswith("#/pictures/"):
            return False

        return parser_extra.get("content_layer") != "furniture"

    def _is_document_index_element(self, element: CanonicalElement) -> bool:
        parser_extra = self._parser_extra(element)
        item_label = str(parser_extra.get("item_label") or "").strip().lower()
        raw_source_type = str(parser_extra.get("raw_source_type") or "").strip().lower()
        return item_label == "document_index" or raw_source_type == "documentindex"

    def _table_fragment_text(self, element: CanonicalElement) -> str | None:
        parser_extra = self._parser_extra(element)
        markdown = clean_chunk_text(parser_extra.get("markdown") or element.text)
        caption = clean_chunk_text(parser_extra.get("caption"))

        if caption and markdown and caption not in markdown:
            return f"{caption}\n{markdown}".strip()

        return markdown or caption

    def _should_chunk_table_element(self, element: CanonicalElement) -> bool:
        parser_extra = self._parser_extra(element)
        column_count = self._coerce_positive_int(parser_extra.get("column_count"))
        row_count = self._coerce_positive_int(parser_extra.get("row_count"))
        markdown = clean_chunk_text(parser_extra.get("markdown") or element.text) or ""

        if column_count is not None and column_count <= 1:
            return False

        if (
            row_count is not None
            and row_count <= 1
            and self.text_splitter.count_tokens(markdown) > 30
        ):
            return False

        return True

    def _table_chunk_type(
        self,
        element: CanonicalElement,
        text: str | None,
    ) -> ChunkType:
        parser_extra = self._parser_extra(element)
        haystack = " ".join(
            part
            for part in [
                clean_chunk_text(parser_extra.get("caption")),
                clean_chunk_text(parser_extra.get("markdown")),
                text,
            ]
            if part
        ).lower()

        spare_part_markers = (
            "spare part",
            "spare parts",
            "part number",
            "part no",
            "| part |",
            "| part number |",
        )
        if any(marker in haystack for marker in spare_part_markers):
            return ChunkType.SPARE_PARTS_TABLE

        return ChunkType.GENERAL

    @staticmethod
    def _parser_extra(element: CanonicalElement) -> dict:
        if element.parser_metadata is None or element.parser_metadata.extra is None:
            return {}

        return element.parser_metadata.extra

    @staticmethod
    def _coerce_positive_int(value: object) -> int | None:
        if value is None:
            return None

        try:
            number = int(value)
        except (TypeError, ValueError):
            return None

        return number if number > 0 else None

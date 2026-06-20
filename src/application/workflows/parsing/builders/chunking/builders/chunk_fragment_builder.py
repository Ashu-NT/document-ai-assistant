from src.application.workflows.parsing.builders.chunking.models.chunk_fragment import (
    ChunkFragment,
)
from src.application.workflows.parsing.builders.chunking.text.chunk_text_splitter import (
    ChunkTextSplitter,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    is_low_value_fragment,
)
from src.domain.common import ChunkType, ElementType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


class ChunkFragmentBuilder:
    def __init__(
        self,
        *,
        text_splitter: ChunkTextSplitter,
        include_picture_chunks: bool = True,
        include_table_context: bool = True,
        asset_context_window: int = 1,
        asset_context_max_tokens: int = 72,
    ) -> None:
        self.text_splitter = text_splitter
        self.include_picture_chunks = include_picture_chunks
        self.include_table_context = include_table_context
        self.asset_context_window = max(0, asset_context_window)
        self.asset_context_max_tokens = max(12, asset_context_max_tokens)

    def build_section_fragments(
        self,
        section: DocumentSection,
        elements: list[CanonicalElement],
    ) -> list[ChunkFragment]:
        fragments: list[ChunkFragment] = []

        for index, element in enumerate(elements):
            fragment = self._build_fragment_from_element(
                section,
                elements,
                index,
                element,
            )
            if fragment is not None:
                fragments.append(fragment)

        return fragments

    def _build_fragment_from_element(
        self,
        section: DocumentSection,
        elements: list[CanonicalElement],
        index: int,
        element: CanonicalElement,
    ) -> ChunkFragment | None:
        if self._is_document_index_element(element):
            return None

        if element.table_id is not None or element.element_type == ElementType.TABLE:
            if not self._should_chunk_table_element(element):
                return None
            text = self._table_fragment_text(elements=elements, index=index, element=element)
            chunk_type = self._table_chunk_type(element, text)
            standalone = True
        elif element.picture_id is not None or element.element_type == ElementType.PICTURE:
            if not self.include_picture_chunks:
                return None
            text = self._picture_fragment_text(
                elements=elements,
                index=index,
                element=element,
            )
            if not text:
                return None
            chunk_type = ChunkType.DRAWING_REFERENCE
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

    def _table_fragment_text(
        self,
        *,
        elements: list[CanonicalElement],
        index: int,
        element: CanonicalElement,
    ) -> str | None:
        parser_extra = self._parser_extra(element)
        markdown = clean_chunk_text(parser_extra.get("markdown") or element.text)
        caption = clean_chunk_text(parser_extra.get("caption"))
        nearby_text = (
            self._nearby_text(elements=elements, index=index)
            if self.include_table_context
            else None
        )

        parts = [part for part in [caption, nearby_text, markdown] if part]
        if not parts:
            return None

        return "\n\n".join(parts).strip()

    def _picture_fragment_text(
        self,
        *,
        elements: list[CanonicalElement],
        index: int,
        element: CanonicalElement,
    ) -> str | None:
        parser_extra = self._parser_extra(element)
        caption = clean_chunk_text(parser_extra.get("caption") or element.text)
        nearby_text = self._nearby_text(elements=elements, index=index)
        ocr_text = clean_chunk_text(parser_extra.get("ocr_text"))
        ocr_text = self._truncate_to_asset_context(ocr_text)

        if not caption and not nearby_text:
            if ocr_text is None or self.text_splitter.count_tokens(ocr_text) < 6:
                return None

        parts: list[str] = []
        if caption:
            parts.append(f"Figure: {caption}")
        if nearby_text:
            parts.append(f"Context: {nearby_text}")
        if ocr_text:
            parts.append(f"OCR: {ocr_text}")

        return "\n\n".join(parts).strip() or None

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

    def _nearby_text(
        self,
        *,
        elements: list[CanonicalElement],
        index: int,
    ) -> str | None:
        if self.asset_context_window <= 0:
            return None

        current_element = elements[index]
        selected_parts: list[str] = []
        token_total = 0
        candidate_indexes = range(
            max(0, index - self.asset_context_window),
            min(len(elements), index + self.asset_context_window + 1),
        )

        for candidate_index in candidate_indexes:
            if candidate_index == index:
                continue

            candidate = elements[candidate_index]
            if not self._element_contributes_to_asset_context(candidate):
                continue

            if not self._shares_page_context(current_element, candidate):
                continue

            text = clean_chunk_text(candidate.text)
            if not text:
                continue

            remaining_tokens = self.asset_context_max_tokens - token_total
            if remaining_tokens <= 0:
                break

            text = self._truncate_to_token_limit(text, remaining_tokens)
            if not text:
                continue

            selected_parts.append(text)
            token_total += self.text_splitter.count_tokens(text)

        if not selected_parts:
            return None

        return clean_chunk_text("\n\n".join(selected_parts))

    @staticmethod
    def _shares_page_context(
        current_element: CanonicalElement,
        candidate: CanonicalElement,
    ) -> bool:
        current_page = current_element.source.page_start
        candidate_page = candidate.source.page_start
        if current_page is None or candidate_page is None:
            return True
        return abs(candidate_page - current_page) <= 1

    def _truncate_to_asset_context(self, text: str | None) -> str | None:
        if not text:
            return None
        return self._truncate_to_token_limit(text, self.asset_context_max_tokens)

    def _truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        tokens = text.split()
        if len(tokens) <= max_tokens:
            return text
        return " ".join(tokens[:max_tokens]).strip()

    def _element_contributes_to_asset_context(
        self,
        element: CanonicalElement,
    ) -> bool:
        if not self._element_contributes_to_chunk(element):
            return False

        return element.element_type in {
            ElementType.TEXT,
            ElementType.LIST_ITEM,
            ElementType.KEY_VALUE,
            ElementType.CODE,
        }

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

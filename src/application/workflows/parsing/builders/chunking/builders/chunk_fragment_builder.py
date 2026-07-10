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
from src.application.workflows.parsing.parsing_value_coercion import (
    coerce_positive_int,
)
from src.domain.common import ChunkType, ElementType
from src.domain.common import DocumentType
from src.domain.document import DocumentSection
from src.domain.elements import CanonicalElement


# A picture whose bounding box covers at least this fraction of its page's
# area is treated as a full-page scan (e.g. a scanned certificate/datasheet
# represented by Docling as one big picture element) rather than a small
# decorative image (logo, letterhead icon). Full-page pictures are kept even
# when include_picture_chunks is False for the document's chunking profile,
# so a scanned document doesn't lose all of its content just because its
# profile suppresses decorative-image noise.
_LARGE_PICTURE_AREA_RATIO = 0.5


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
        self.include_table_context = include_table_context
        self.asset_context_window = max(0, asset_context_window)
        self.asset_context_max_tokens = max(12, asset_context_max_tokens)
        self.page_sizes = page_sizes or {}
        self.structured_fragment_builder = (
            structured_fragment_builder
            or StructuredSectionFragmentBuilder(
                text_splitter=text_splitter,
            )
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
            if not self._should_chunk_table_element(element):
                return None
            text = self._table_fragment_text(elements=elements, index=index, element=element)
            chunk_type = self._table_chunk_type(element, text)
            standalone = True
            table_rows = self._parser_extra(element).get("table_rows") or None
        elif element.picture_id is not None or element.element_type == ElementType.PICTURE:
            if not self.include_picture_chunks and not self._is_large_picture(element):
                return None
            text = self._picture_fragment_text(
                elements=elements,
                index=index,
                element=element,
            )
            if not text:
                return None
            chunk_type = self._picture_chunk_type(text)
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

    def _is_large_picture(self, element: CanonicalElement) -> bool:
        bbox = element.source.bbox
        if bbox is None:
            return False

        page_no = element.source.page_start
        if page_no is None:
            return False

        page_size = self.page_sizes.get(page_no)
        if page_size is None:
            return False

        width, height = page_size
        page_area = width * height
        if page_area <= 0:
            return False

        bbox_area = abs(bbox.x2 - bbox.x1) * abs(bbox.y2 - bbox.y1)
        return (bbox_area / page_area) >= _LARGE_PICTURE_AREA_RATIO

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
        ocr_text, ocr_token_count = self._truncate_to_asset_context(ocr_text)

        if not caption and not nearby_text:
            if ocr_text is None or ocr_token_count < 6:
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
        column_count = coerce_positive_int(parser_extra.get("column_count"))
        row_count = coerce_positive_int(parser_extra.get("row_count"))
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

        if self._has_spare_part_header_row(parser_extra):
            return ChunkType.SPARE_PARTS_TABLE

        return ChunkType.GENERAL

    @staticmethod
    def _has_spare_part_header_row(parser_extra: dict) -> bool:
        table_rows = parser_extra.get("table_rows")
        if not table_rows:
            return False

        header_row = table_rows[0]
        spare_part_header_markers = ("part", "spare part", "part number")
        return any(
            any(marker in cell.strip().lower() for marker in spare_part_header_markers)
            for cell in header_row
        )

    @staticmethod
    def _picture_chunk_type(text: str | None) -> ChunkType:
        """Classify picture/figure chunks by their extracted text content.

        Figures containing oil-quantity or lubricant-specification data (common in
        service manuals as scanned tables) are maintenance intervals, not drawing
        references.  All other figures keep the drawing_reference default.
        """
        if not text:
            return ChunkType.DRAWING_REFERENCE
        lowered = text.lower()
        maintenance_signals = (
            "oil quantity",
            "oil specification",
            "oil capacity",
            "lubricant",
            "lubrication",
            "grease quantity",
            "grease specification",
            "service fill",
            "fluid capacity",
            "fluid specification",
        )
        if any(signal in lowered for signal in maintenance_signals):
            return ChunkType.MAINTENANCE_INTERVAL
        return ChunkType.DRAWING_REFERENCE

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

            text, text_token_count = self._truncate_to_token_limit(text, remaining_tokens)
            if not text:
                continue

            selected_parts.append(text)
            token_total += text_token_count

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

    def _truncate_to_asset_context(self, text: str | None) -> tuple[str | None, int]:
        if not text:
            return None, 0
        return self._truncate_to_token_limit(text, self.asset_context_max_tokens)

    def _truncate_to_token_limit(self, text: str, max_tokens: int) -> tuple[str, int]:
        return self.text_splitter.token_counter.truncate_to_tokens_with_count(
            text, max_tokens
        )

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
        return resolve_parser_extra(element)

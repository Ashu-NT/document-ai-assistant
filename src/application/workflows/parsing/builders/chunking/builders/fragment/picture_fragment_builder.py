from src.application.workflows.parsing.builders.chunking.builders.fragment.asset_context_resolver import (
    AssetContextResolver,
)
from src.application.workflows.parsing.builders.chunking.text.chunking_utils import (
    clean_chunk_text,
    resolve_parser_extra,
)
from src.domain.common import ChunkType
from src.domain.elements import CanonicalElement

# A picture whose bounding box covers at least this fraction of its page's
# area is treated as a full-page scan (e.g. a scanned certificate/datasheet
# represented by Docling as one big picture element) rather than a small
# decorative image (logo, letterhead icon). Full-page pictures are kept even
# when include_picture_chunks is False for the document's chunking profile,
# so a scanned document doesn't lose all of its content just because its
# profile suppresses decorative-image noise.
_LARGE_PICTURE_AREA_RATIO = 0.5


class PictureFragmentBuilder:
    """Builds fragment text and classifies chunk type for picture elements."""

    def __init__(
        self,
        *,
        page_sizes: dict[int, tuple[float, float]],
        asset_context_resolver: AssetContextResolver,
    ) -> None:
        self.page_sizes = page_sizes
        self.asset_context_resolver = asset_context_resolver

    def is_large_picture(self, element: CanonicalElement) -> bool:
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

    def picture_fragment_text(
        self,
        *,
        elements: list[CanonicalElement],
        index: int,
        element: CanonicalElement,
    ) -> str | None:
        parser_extra = resolve_parser_extra(element)
        caption = clean_chunk_text(parser_extra.get("caption") or element.text)
        nearby_text = self.asset_context_resolver.nearby_text(
            elements=elements, index=index
        )
        raw_ocr_text = clean_chunk_text(parser_extra.get("ocr_text"))
        ocr_text, _ = self.asset_context_resolver.truncate_to_asset_context(
            raw_ocr_text
        )

        if not caption and not nearby_text:
            # Word count of the pre-truncation OCR text, not the post-
            # truncation token count: this is a "is there enough raw OCR
            # substance to bother" gate, not an embedding-budget check, so
            # it must stay stable regardless of which ChunkTokenCounter is
            # configured for the asset-context truncation above.
            if ocr_text is None or raw_ocr_text is None or len(raw_ocr_text.split()) < 6:
                return None

        parts: list[str] = []
        if caption:
            parts.append(f"Figure: {caption}")
        if nearby_text:
            parts.append(f"Context: {nearby_text}")
        if ocr_text:
            parts.append(f"OCR: {ocr_text}")

        return "\n\n".join(parts).strip() or None

    @staticmethod
    def picture_chunk_type(text: str | None) -> ChunkType:
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

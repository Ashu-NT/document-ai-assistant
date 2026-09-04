from dataclasses import dataclass
from typing import Literal

from src.domain.common import BoundingBox


@dataclass(slots=True, frozen=True)
class PdfLinkAnnotation:
    """One same-document internal PDF link annotation, as extracted directly
    from the PDF's own structure (not text). Pages are 1-based throughout."""

    source_page: int
    dest_page: int
    # Which pdfium API path resolved the destination.
    link_kind: Literal["direct_destination", "goto"]
    # Captured purely as inert provenance for a possible future bbox-matching
    # phase - never used for resolution in this version.
    source_rect: BoundingBox
    rect_coordinate_origin: str
    source_page_size: tuple[float, float]
    source_page_rotation_degrees: int
    source_page_label: str | None
    dest_page_label: str | None


__all__ = ["PdfLinkAnnotation"]

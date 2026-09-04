from dataclasses import dataclass
from typing import Literal

from src.domain.common import BoundingBox


@dataclass(slots=True, frozen=True)
class PdfLinkProvenance:
    """Inert, audit-only detail about the PDF link annotation a
    PDF_LINK_REFERENCE (or a CONFIRMED row corroborated by one) was built
    from. Never used for resolution - source_rect is captured purely as
    groundwork for a possible future bbox-matching phase."""

    # The exact page the link annotation was found on. source_chunk_id alone
    # doesn't identify this for a multi-page chunk (page_start != page_end).
    source_page: int
    # Which pdfium API path resolved the destination.
    link_kind: Literal["direct_destination", "goto"]
    source_rect: BoundingBox
    rect_coordinate_origin: str
    source_page_size: tuple[float, float]
    source_page_rotation_degrees: int
    source_page_label: str | None
    dest_page_label: str | None


__all__ = ["PdfLinkProvenance"]

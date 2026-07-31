from dataclasses import dataclass

from src.domain.common import BoundingBox


@dataclass(slots=True, frozen=True)
class RowBoundingBox:
    row_index: int
    page_number: int | None
    bbox: BoundingBox

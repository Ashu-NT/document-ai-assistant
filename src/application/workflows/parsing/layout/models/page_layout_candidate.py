from dataclasses import dataclass

from src.domain.common import BoundingBox


@dataclass(frozen=True, slots=True)
class PageLayoutCandidate:
    element_ref: str
    page_number: int
    bbox: BoundingBox | None
    label: str
    text: str | None = None
    content_layer: str | None = None

    def center_x(self) -> float | None:
        if self.bbox is None:
            return None
        return (self.bbox.x1 + self.bbox.x2) / 2.0

    def top_y(self) -> float | None:
        if self.bbox is None:
            return None
        return min(self.bbox.y1, self.bbox.y2)

    def width(self) -> float | None:
        if self.bbox is None:
            return None
        return abs(self.bbox.x2 - self.bbox.x1)

    def height(self) -> float | None:
        if self.bbox is None:
            return None
        return abs(self.bbox.y2 - self.bbox.y1)

    def bottom_y(self) -> float | None:
        if self.bbox is None:
            return None
        return max(self.bbox.y1, self.bbox.y2)

    def spans_split(self, split_x: float) -> bool:
        if self.bbox is None:
            return False
        return self.bbox.x1 < split_x < self.bbox.x2

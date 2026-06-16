from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(slots=True)
class SourceLocation:
    page_start: int | None = None
    page_end: int | None = None
    bbox: BoundingBox | None = None
    
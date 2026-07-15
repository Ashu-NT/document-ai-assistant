from dataclasses import dataclass, field

from src.application.workflows.parsing.layout.models.layout_region_role import (
    LayoutRegionRole,
)
from src.domain.common import BoundingBox


@dataclass(slots=True)
class PageLayoutRegion:
    region_id: str
    page_number: int
    role: LayoutRegionRole
    lane_index: int | None
    lane_count: int
    bbox: BoundingBox | None
    element_refs: tuple[str, ...]
    reading_order_by_element_ref: dict[str, int] = field(default_factory=dict)

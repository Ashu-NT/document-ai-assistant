from dataclasses import dataclass, field

from src.application.workflows.parsing.layout.models.page_layout_region import (
    PageLayoutRegion,
)


@dataclass(slots=True)
class PageLayoutAnalysis:
    page_number: int
    page_width: float | None
    page_height: float | None
    orientation: str | None
    is_front_matter: bool
    regions: tuple[PageLayoutRegion, ...] = field(default_factory=tuple)

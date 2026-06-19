from dataclasses import dataclass, field
from typing import Any

from src.domain.common import BoundingBox, ElementType


@dataclass(slots=True)
class CanonicalElement:
    element_id: str
    document_id: str
    element_type: ElementType
    text: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    bbox: BoundingBox | None = None
    order_index: int = 0
    section_title: str | None = None
    section_path: list[str] = field(default_factory=list)
    parent_section_id: str | None = None
    raw_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

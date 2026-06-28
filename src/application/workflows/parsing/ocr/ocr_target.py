from dataclasses import dataclass, field
from typing import Any

from src.application.workflows.parsing.ocr.ocr_target_type import OCRTargetType
from src.domain.common import BoundingBox


@dataclass(slots=True)
class OCRTarget:
    target_id: str
    target_type: OCRTargetType
    document_path: str
    page_number: int | None = None
    image_path: str | None = None
    bbox: BoundingBox | None = None
    source_element_id: str | None = None
    reason: str = ""
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


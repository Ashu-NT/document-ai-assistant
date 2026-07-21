from dataclasses import dataclass, field

from src.application.workflows.parsing.canonical_element import CanonicalElement
from src.application.workflows.parsing.ocr.ocr_trace import OCRTrace


@dataclass(slots=True)
class OCRMergeResult:
    canonical_elements: list[CanonicalElement]
    ocr_trace: OCRTrace
    warnings: list[str] = field(default_factory=list)
    added_synthetic_elements: int = 0
    updated_asset_elements: int = 0


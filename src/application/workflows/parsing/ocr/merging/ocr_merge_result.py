from dataclasses import dataclass, field

from src.application.workflows.parsing.parsed_canonical_element import ParsedCanonicalElement
from src.application.workflows.parsing.ocr.merging.ocr_trace import OCRTrace


@dataclass(slots=True)
class OCRMergeResult:
    canonical_elements: list[ParsedCanonicalElement]
    ocr_trace: OCRTrace
    warnings: list[str] = field(default_factory=list)
    added_synthetic_elements: int = 0
    updated_asset_elements: int = 0


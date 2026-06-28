from dataclasses import dataclass, field

from src.application.workflows.parsing.ocr.ocr_target import OCRTarget
from src.application.workflows.parsing.ocr.page_text_quality import PageTextQuality


@dataclass(slots=True)
class OCRSelectionResult:
    page_analyses: list[PageTextQuality] = field(default_factory=list)
    targets: list[OCRTarget] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


from dataclasses import dataclass

from src.application.contracts.ai import OCRResult
from src.application.workflows.parsing.ocr.ocr_target import OCRTarget


@dataclass(slots=True)
class OCRTargetExecutionResult:
    target: OCRTarget
    source_image_path: str | None = None
    ocr_result: OCRResult | None = None
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.ocr_result is not None and self.error is None


from dataclasses import dataclass


@dataclass(slots=True)
class OCRMergePolicy:
    min_confidence: float = 0.5
    attach_low_confidence_text: bool = False


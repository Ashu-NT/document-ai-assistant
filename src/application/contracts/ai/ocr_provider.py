from typing import Protocol

from src.application.contracts.ai.ocr_result import OCRResult


class OCRProvider(Protocol):
    def extract_text_from_image(self, image_path: str) -> OCRResult | str:
        ...

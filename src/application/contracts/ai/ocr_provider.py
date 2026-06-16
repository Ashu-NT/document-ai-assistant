from typing import Protocol


class OCRProvider(Protocol):
    def extract_text_from_image(self, image_path: str) -> str:
        ...
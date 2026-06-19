import pytest

from src.application.services.ai import OCRService
from src.shared.exceptions import OCRProviderError


class FakeOCRProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def extract_text_from_image(self, image_path: str) -> str:
        self.calls.append(image_path)
        return "FILTER HOUSING HP-001"


class FailingOCRProvider:
    def extract_text_from_image(self, image_path: str) -> str:
        raise OCRProviderError("OCR provider failed.")


def test_extract_text_from_image_calls_provider() -> None:
    provider = FakeOCRProvider()
    service = OCRService(provider)

    result = service.extract_text_from_image("outputs/images/pic_001.png")

    assert result == "FILTER HOUSING HP-001"
    assert provider.calls == ["outputs/images/pic_001.png"]


def test_extract_text_from_image_does_not_swallow_errors() -> None:
    service = OCRService(FailingOCRProvider())

    with pytest.raises(OCRProviderError):
        service.extract_text_from_image("outputs/images/pic_001.png")

import pytest

from src.application.services.ai import OCRResult, OCRService
from src.shared.exceptions import OCRProviderError


class FakeOCRProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def extract_text_from_image(self, image_path: str) -> OCRResult:
        self.calls.append(image_path)
        return OCRResult(
            text="FILTER HOUSING HP-001",
            provider_name="FakeOCRProvider",
            confidence=0.97,
            source_image_path=image_path,
        )


class StringOCRProvider:
    def extract_text_from_image(self, image_path: str) -> str:
        return "PLAIN TEXT RESULT"


class FailingOCRProvider:
    def extract_text_from_image(self, image_path: str) -> OCRResult:
        raise OCRProviderError("OCR provider failed.")


def test_extract_text_from_image_calls_provider() -> None:
    provider = FakeOCRProvider()
    service = OCRService(provider)

    result = service.extract_text_from_image("outputs/images/pic_001.png")

    assert result == "FILTER HOUSING HP-001"
    assert provider.calls == ["outputs/images/pic_001.png"]


def test_extract_result_from_image_normalizes_string_provider_output() -> None:
    service = OCRService(StringOCRProvider())

    result = service.extract_result_from_image("outputs/images/pic_001.png")

    assert result.text == "PLAIN TEXT RESULT"
    assert result.provider_name == "StringOCRProvider"
    assert result.source_image_path == "outputs/images/pic_001.png"


def test_extract_text_from_image_does_not_swallow_errors() -> None:
    service = OCRService(FailingOCRProvider())

    with pytest.raises(OCRProviderError):
        service.extract_text_from_image("outputs/images/pic_001.png")

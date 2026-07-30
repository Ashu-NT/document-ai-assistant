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


class FlakyOCRProvider:
    def __init__(self, *, failures_before_success: int) -> None:
        self.failures_before_success = failures_before_success
        self.calls = 0

    def extract_text_from_image(self, image_path: str) -> OCRResult:
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise OCRProviderError("transient OCR failure")
        return OCRResult(
            text="RECOVERED",
            provider_name="FlakyOCRProvider",
            source_image_path=image_path,
        )


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


def test_extract_text_from_image_does_not_retry_by_default() -> None:
    provider = FlakyOCRProvider(failures_before_success=1)
    service = OCRService(provider)

    with pytest.raises(OCRProviderError):
        service.extract_text_from_image("outputs/images/pic_001.png")

    assert provider.calls == 1


def test_extract_text_from_image_retries_transient_failures() -> None:
    provider = FlakyOCRProvider(failures_before_success=2)
    service = OCRService(provider, retry_attempts=3, retry_backoff_seconds=0)

    result = service.extract_text_from_image("outputs/images/pic_001.png")

    assert result == "RECOVERED"
    assert provider.calls == 3


def test_extract_text_from_image_raises_after_exhausting_retries() -> None:
    provider = FlakyOCRProvider(failures_before_success=99)
    service = OCRService(provider, retry_attempts=2, retry_backoff_seconds=0)

    with pytest.raises(OCRProviderError):
        service.extract_text_from_image("outputs/images/pic_001.png")

    assert provider.calls == 3

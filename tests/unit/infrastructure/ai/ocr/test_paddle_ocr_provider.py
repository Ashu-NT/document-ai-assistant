import pytest

from src.infrastructure.ai.ocr import PaddleOCRProvider
from src.shared.exceptions import OCRProviderError


class FakeOCRResult:
    def __init__(self, rec_texts) -> None:
        self.rec_texts = rec_texts


class FakePaddleOCREngine:
    def __init__(self, result) -> None:
        self.result = result
        self.calls: list[str] = []

    def ocr(self, image_path: str):
        self.calls.append(image_path)
        return self.result


class FailingPaddleOCREngine:
    def ocr(self, image_path: str):
        raise RuntimeError("ocr failed")


def test_extract_text_from_image_calls_paddle_ocr() -> None:
    engine = FakePaddleOCREngine(
        [
            {"rec_texts": ["FILTER", "HOUSING"]},
            {"rec_texts": ["HP-001"]},
        ]
    )
    provider = PaddleOCRProvider(ocr_engine=engine)

    result = provider.extract_text_from_image("outputs/images/pic_001.png")

    assert result == "FILTER\nHOUSING\nHP-001"
    assert engine.calls == ["outputs/images/pic_001.png"]


def test_extract_text_from_image_normalizes_object_results() -> None:
    engine = FakePaddleOCREngine([FakeOCRResult([("FILTER", 0.99), "HP-001"])])
    provider = PaddleOCRProvider(ocr_engine=engine)

    result = provider.extract_text_from_image("outputs/images/pic_001.png")

    assert result == "FILTER\nHP-001"


def test_extract_text_from_image_wraps_underlying_errors() -> None:
    provider = PaddleOCRProvider(ocr_engine=FailingPaddleOCREngine())

    with pytest.raises(OCRProviderError):
        provider.extract_text_from_image("outputs/images/pic_001.png")

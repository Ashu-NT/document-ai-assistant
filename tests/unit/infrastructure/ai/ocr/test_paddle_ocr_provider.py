import pytest

from src.application.contracts.ai import OCRResult
from src.infrastructure.ai.ocr import PaddleOCRProvider
from src.infrastructure.ai.ocr import paddle_ocr_provider
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

    assert isinstance(result, OCRResult)
    assert result.text == "FILTER\nHOUSING\nHP-001"
    assert result.provider_name == "PaddleOCRProvider"
    assert engine.calls == ["outputs/images/pic_001.png"]


def test_extract_text_from_image_normalizes_object_results() -> None:
    engine = FakePaddleOCREngine([FakeOCRResult([("FILTER", 0.99), "HP-001"])])
    provider = PaddleOCRProvider(ocr_engine=engine)

    result = provider.extract_text_from_image("outputs/images/pic_001.png")

    assert result.text == "FILTER\nHP-001"
    assert result.confidence == pytest.approx(0.99)


def test_extract_text_from_image_wraps_underlying_errors() -> None:
    provider = PaddleOCRProvider(ocr_engine=FailingPaddleOCREngine())

    with pytest.raises(OCRProviderError):
        provider.extract_text_from_image("outputs/images/pic_001.png")


def test_provider_uses_settings_defaults_when_arguments_are_omitted(
    monkeypatch,
) -> None:
    fake_settings = type(
        "FakeOCRSettings",
        (),
        {
            "paddle_lang": "de",
            "paddle_use_textline_orientation": False,
            "paddle_ocr_version": "PP-OCRv5",
        },
    )()
    monkeypatch.setattr(
        paddle_ocr_provider,
        "ocr_settings",
        fake_settings,
    )

    provider = PaddleOCRProvider()

    assert provider.lang == "de"
    assert provider.use_textline_orientation is False
    assert provider.ocr_version == "PP-OCRv5"

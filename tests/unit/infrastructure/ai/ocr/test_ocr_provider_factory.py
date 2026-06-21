import pytest

from src.infrastructure.ai.ocr import ocr_provider_factory
from src.infrastructure.ai.ocr import build_ocr_provider
from src.infrastructure.ai.ocr import PaddleOCRProvider
from src.shared.exceptions import InfrastructureError


def test_build_ocr_provider_returns_paddleocr_provider(monkeypatch) -> None:
    fake_settings = type(
        "FakeOCRSettings",
        (),
        {"provider": "paddleocr"},
    )()
    monkeypatch.setattr(
        ocr_provider_factory,
        "ocr_settings",
        fake_settings,
    )

    provider = build_ocr_provider()

    assert isinstance(provider, PaddleOCRProvider)


def test_build_ocr_provider_rejects_unsupported_provider(monkeypatch) -> None:
    fake_settings = type(
        "FakeOCRSettings",
        (),
        {"provider": "rapidocr"},
    )()
    monkeypatch.setattr(
        ocr_provider_factory,
        "ocr_settings",
        fake_settings,
    )

    with pytest.raises(InfrastructureError) as exc_info:
        build_ocr_provider()

    assert exc_info.value.details == {
        "ocr_provider": "rapidocr",
        "supported_providers": ["paddleocr"],
    }

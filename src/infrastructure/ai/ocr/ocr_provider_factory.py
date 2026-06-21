from src.application.contracts.ai import OCRProvider
from src.config.settings import ocr_settings
from src.infrastructure.ai.ocr.paddle_ocr_provider import PaddleOCRProvider
from src.shared.exceptions import InfrastructureError


def build_ocr_provider() -> OCRProvider:
    normalized_provider = ocr_settings.provider.strip().lower()

    if normalized_provider in {"", "paddleocr"}:
        return PaddleOCRProvider()

    raise InfrastructureError(
        "Unsupported OCR provider configured.",
        details={
            "ocr_provider": ocr_settings.provider,
            "supported_providers": ["paddleocr"],
        },
    )

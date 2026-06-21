from pydantic import Field

from src.config.settings.base_settings import AppBaseSettings


class OCRSettings(AppBaseSettings):
    enabled: bool = Field(
        default=False,
        alias="ENABLE_PROVIDER_OCR",
    )

    provider: str = Field(
        default="paddleocr",
        alias="OCR_PROVIDER",
    )

    paddle_lang: str = Field(
        default="en",
        alias="PADDLE_OCR_LANG",
    )

    paddle_use_textline_orientation: bool = Field(
        default=True,
        alias="PADDLE_OCR_USE_TEXTLINE_ORIENTATION",
    )

    paddle_ocr_version: str | None = Field(
        default=None,
        alias="PADDLE_OCR_VERSION",
    )

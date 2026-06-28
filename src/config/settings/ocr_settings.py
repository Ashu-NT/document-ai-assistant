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

    asset_enabled: bool = Field(
        default=True,
        alias="OCR_ASSET_ENABLED",
    )

    page_fallback_enabled: bool = Field(
        default=False,
        alias="OCR_PAGE_FALLBACK_ENABLED",
    )

    region_fallback_enabled: bool = Field(
        default=False,
        alias="OCR_REGION_FALLBACK_ENABLED",
    )

    max_pages_per_document: int = Field(
        default=3,
        alias="OCR_MAX_PAGES_PER_DOCUMENT",
    )

    max_regions_per_page: int = Field(
        default=2,
        alias="OCR_MAX_REGIONS_PER_PAGE",
    )

    min_text_chars_per_page: int = Field(
        default=120,
        alias="OCR_MIN_TEXT_CHARS_PER_PAGE",
    )

    min_text_density: float = Field(
        default=0.0025,
        alias="OCR_MIN_TEXT_DENSITY",
    )

    min_image_area_ratio: float = Field(
        default=0.35,
        alias="OCR_MIN_IMAGE_AREA_RATIO",
    )

    page_render_dpi: int = Field(
        default=150,
        alias="OCR_PAGE_RENDER_DPI",
    )

    timeout_seconds: int = Field(
        default=30,
        alias="OCR_TIMEOUT_SECONDS",
    )

    min_confidence: float = Field(
        default=0.5,
        alias="OCR_MIN_CONFIDENCE",
    )

    attach_low_confidence_text: bool = Field(
        default=False,
        alias="OCR_ATTACH_LOW_CONFIDENCE_TEXT",
    )

    output_dir: str = Field(
        default="outputs/debug_ocr",
        alias="OCR_OUTPUT_DIR",
    )

    trace_enabled: bool = Field(
        default=False,
        alias="OCR_TRACE_ENABLED",
    )

    fail_fast: bool = Field(
        default=False,
        alias="OCR_FAIL_FAST",
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

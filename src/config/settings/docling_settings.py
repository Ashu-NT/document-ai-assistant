from pydantic import Field

from src.config.settings.base_settings import AppBaseSettings


class DoclingSettings(AppBaseSettings):
    images_scale: float = Field(
        default=1.0,
        alias="DOCLING_IMAGES_SCALE",
    )

    num_threads: int = Field(
        default=1,
        alias="DOCLING_NUM_THREADS",
    )

    enable_table_structure: bool = Field(
        default=True,
        alias="DOCLING_ENABLE_TABLE_STRUCTURE",
    )

    enable_ocr: bool = Field(
        default=True,
        alias="DOCLING_ENABLE_OCR",
    )

    ocr_engine: str = Field(
        default="auto",
        alias="DOCLING_OCR_ENGINE",
    )

    rapidocr_backend: str = Field(
        default="torch",
        alias="DOCLING_RAPIDOCR_BACKEND",
    )

    force_full_page_ocr: bool = Field(
        default=False,
        alias="DOCLING_FORCE_FULL_PAGE_OCR",
    )

    bitmap_area_threshold: float = Field(
        default=0.05,
        alias="DOCLING_BITMAP_AREA_THRESHOLD",
    )

    ocr_batch_size: int = Field(
        default=4,
        alias="DOCLING_OCR_BATCH_SIZE",
    )

    export_markdown: bool = Field(
        default=True,
        alias="DOCLING_EXPORT_MARKDOWN",
    )

    export_json: bool = Field(
        default=True,
        alias="DOCLING_EXPORT_JSON",
    )

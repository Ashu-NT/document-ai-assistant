from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class IngestionSettings(AppBaseSettings):
    max_file_size_mb: int = Field(alias="MAX_FILE_SIZE_MB")

    max_pdf_pages: int = Field(alias="MAX_PDF_PAGES")

    enable_image_extraction: bool = Field(
        alias="ENABLE_IMAGE_EXTRACTION"
    )

    enable_table_extraction: bool = Field(
        alias="ENABLE_TABLE_EXTRACTION"
    )

    enable_question_generation: bool = Field(
        default=False,
        alias="ENABLE_QUESTION_GENERATION"
    )

        

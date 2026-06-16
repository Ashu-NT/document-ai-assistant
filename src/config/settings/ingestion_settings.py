from pydantic import Field
from pydantic_settings import BaseSettings


class IngestionSettings(BaseSettings):
    max_file_size_mb: int = Field(alias="MAX_FILE_SIZE_MB")

    max_pdf_pages: int = Field(alias="MAX_PDF_PAGES")

    enable_image_extraction: bool = Field(
        alias="ENABLE_IMAGE_EXTRACTION"
    )

    enable_table_extraction: bool = Field(
        alias="ENABLE_TABLE_EXTRACTION"
    )

    enable_question_generation: bool = Field(
        alias="ENABLE_QUESTION_GENERATION"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"
        
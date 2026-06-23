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

    enable_answer_generation: bool = Field(
        default=False,
        alias="ENABLE_ANSWER_GENERATION"
    )

    max_chunk_tokens: int = Field(
        default=1000,
        alias="MAX_CHUNK_TOKENS"
    )

    chunk_overlap: int = Field(
        default=150,
        alias="CHUNK_OVERLAP"
    )

    min_section_text_length: int = Field(
        default=150,
        alias="MIN_SECTION_TEXT_LENGTH"
    )


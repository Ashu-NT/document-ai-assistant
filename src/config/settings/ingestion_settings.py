from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class IngestionSettings(AppBaseSettings):
    ingestion_runtime_profile: str = Field(
        default="auto",
        alias="INGESTION_RUNTIME_PROFILE",
    )

    max_file_size_mb: int = Field(alias="MAX_FILE_SIZE_MB")

    max_pdf_pages: int = Field(alias="MAX_PDF_PAGES")

    parse_timeout_seconds: int = Field(
        default=600,
        alias="PARSE_TIMEOUT_SECONDS",
    )

    low_confidence_parse_threshold: float = Field(
        default=0.5,
        alias="LOW_CONFIDENCE_PARSE_THRESHOLD",
    )

    enable_question_generation: bool = Field(
        default=False,
        alias="ENABLE_QUESTION_GENERATION"
    )

    enable_answer_generation: bool = Field(
        default=False,
        alias="ENABLE_ANSWER_GENERATION"
    )

    # These three are global overrides for the per-document-type chunking
    # profiles (src/config/chunking/*.yaml). Leave unset (None) so each
    # document type's own tuned profile takes effect; only set one of these
    # to force the same value across every document type regardless of
    # profile.
    max_chunk_tokens: int | None = Field(
        default=None,
        alias="MAX_CHUNK_TOKENS"
    )

    chunk_overlap: int | None = Field(
        default=None,
        alias="CHUNK_OVERLAP"
    )

    min_section_text_length: int | None = Field(
        default=None,
        alias="MIN_SECTION_TEXT_LENGTH"
    )


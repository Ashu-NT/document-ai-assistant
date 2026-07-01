from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class ExtractionSettings(AppBaseSettings):
    extraction_enabled: bool = Field(
        alias="EXTRACTION_ENABLED"
    )

    extraction_confidence_threshold: float = Field(
        alias="EXTRACTION_CONFIDENCE_THRESHOLD"
    )

    extraction_require_human_review: bool = Field(
        alias="EXTRACTION_REQUIRE_HUMAN_REVIEW"
    )
    extraction_max_chunks_per_batch: int = Field(
        default=8,
        alias="EXTRACTION_MAX_CHUNKS_PER_BATCH",
    )

    extraction_max_chars_per_batch: int = Field(
        default=8000,
        alias="EXTRACTION_MAX_CHARS_PER_BATCH",
    )

    extraction_allow_partial_batches: bool = Field(
        default=False,
        alias="EXTRACTION_ALLOW_PARTIAL_BATCHES",
    )

    extraction_failure_preview_chars: int = Field(
        default=1200,
        alias="EXTRACTION_FAILURE_PREVIEW_CHARS",
    )

    extraction_max_attempts: int = Field(
        default=2,
        alias="EXTRACTION_MAX_ATTEMPTS",
    )

    extraction_temperature: float = Field(
        default=0.0,
        alias="EXTRACTION_TEMPERATURE",
    )

    extraction_json_mode: bool = Field(
        default=True,
        alias="EXTRACTION_JSON_MODE",
    )

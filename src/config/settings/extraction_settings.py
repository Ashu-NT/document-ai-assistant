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
        
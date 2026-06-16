from pydantic import Field
from pydantic_settings import BaseSettings


class ExtractionSettings(BaseSettings):
    extraction_enabled: bool = Field(
        alias="EXTRACTION_ENABLED"
    )

    extraction_confidence_threshold: float = Field(
        alias="EXTRACTION_CONFIDENCE_THRESHOLD"
    )

    extraction_require_human_review: bool = Field(
        alias="EXTRACTION_REQUIRE_HUMAN_REVIEW"
    )

    class Config:
        env_file = ".env"
        
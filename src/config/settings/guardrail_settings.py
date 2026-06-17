from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class GuardrailSettings(AppBaseSettings):
    min_evidence_chunks: int = Field(
        alias="MIN_EVIDENCE_CHUNKS"
    )

    require_citations: bool = Field(
        alias="REQUIRE_CITATIONS"
    )

        
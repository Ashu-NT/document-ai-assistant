from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class GuardrailSettings(AppBaseSettings):
    min_evidence_chunks: int = Field(
        alias="MIN_EVIDENCE_CHUNKS"
    )

    require_citations: bool = Field(
        alias="REQUIRE_CITATIONS"
    )

    min_claim_support_score: float = Field(
        default=0.60,
        alias="ANSWER_MIN_CLAIM_SUPPORT_SCORE"
    )

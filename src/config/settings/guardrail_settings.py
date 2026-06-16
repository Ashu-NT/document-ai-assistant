from pydantic import Field
from pydantic_settings import BaseSettings


class GuardrailSettings(BaseSettings):
    min_evidence_chunks: int = Field(
        alias="MIN_EVIDENCE_CHUNKS"
    )

    require_citations: bool = Field(
        alias="REQUIRE_CITATIONS"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"
        
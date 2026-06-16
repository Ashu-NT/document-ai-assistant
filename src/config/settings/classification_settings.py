from pydantic import Field
from pydantic_settings import BaseSettings


class ClassificationSettings(BaseSettings):

    enabled: bool = Field(
        alias="CLASSIFICATION_ENABLED"
    )

    classification_llm: str = Field(
        alias="CLASSIFICATION_LLM"
    )

    confidence_threshold: float = Field(
        alias="CLASSIFICATION_CONFIDENCE_THRESHOLD"
    )

    store_reasoning: bool = Field(
        alias="CLASSIFICATION_STORE_REASONING"
    )

    allow_reclassification: bool = Field(
        alias="CLASSIFICATION_ALLOW_RECLASSIFICATION"
    )

    use_rules: bool = Field(
        alias="CLASSIFICATION_USE_RULES"
    )

    use_llm: bool = Field(
        alias="CLASSIFICATION_USE_LLM"
    )

    use_cache: bool = Field(
        alias="CLASSIFICATION_USE_CACHE"
    )

    max_text_length: int = Field(
        alias="CLASSIFICATION_MAX_TEXT_LENGTH"
    )

    document_types: str = Field(
        alias="DOCUMENT_TYPES"
    )

    chunk_classification_enabled: bool = Field(
        alias="CHUNK_CLASSIFICATION_ENABLED"
    )

    chunk_classification_llm: str = Field(
        alias="CHUNK_CLASSIFICATION_LLM"
    )

    chunk_confidence_threshold: float = Field(
        alias="CHUNK_CLASSIFICATION_CONFIDENCE_THRESHOLD"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def supported_document_types(self) -> list[str]:
        return [
            item.strip()
            for item in self.document_types.split(",")
        ]
        
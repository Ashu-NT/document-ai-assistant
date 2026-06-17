from pydantic import Field
from src.config.settings.base_settings import AppBaseSettings


class EmbeddingSettings(AppBaseSettings):
    model_name: str = Field(alias="EMBEDDING_MODEL")

    dimensions: int = Field(alias="EMBEDDING_DIMENSIONS")

        
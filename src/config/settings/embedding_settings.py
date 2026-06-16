from pydantic import Field
from pydantic_settings import BaseSettings


class EmbeddingSettings(BaseSettings):
    model_name: str = Field(alias="EMBEDDING_MODEL")

    dimensions: int = Field(alias="EMBEDDING_DIMENSIONS")

    class Config:
        env_file = ".env"
        extra = "ignore"
        
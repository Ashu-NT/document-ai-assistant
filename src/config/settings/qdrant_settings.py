from pydantic import Field
from pydantic_settings import BaseSettings


class QdrantSettings(BaseSettings):
    mode: str = Field(alias="QDRANT_MODE")
    path: str = Field(alias="QDRANT_PATH")
    host: str = Field(alias="QDRANT_HOST")
    port: int = Field(alias="QDRANT_PORT")
    collection: str = Field(alias="QDRANT_COLLECTION")

    class Config:
        env_file = ".env"
        extra = "ignore"
        
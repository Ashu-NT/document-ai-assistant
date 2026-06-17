from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.config.paths import resolve_project_path


class QdrantSettings(BaseSettings):
    mode: str = Field(alias="QDRANT_MODE")
    path: str = Field(alias="QDRANT_PATH")
    host: str = Field(alias="QDRANT_HOST")
    port: int = Field(alias="QDRANT_PORT")
    collection: str = Field(alias="QDRANT_COLLECTION")
    vector_distance: str = Field(default="cosine", alias="QDRANT_VECTOR_DISTANCE")

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def storage_path(self) -> Path:
        return resolve_project_path(self.path)

    def ensure_storage_directory(self) -> None:
        self.storage_path.mkdir(parents=True, exist_ok=True)
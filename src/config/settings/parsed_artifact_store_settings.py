from pathlib import Path

from pydantic import Field

from src.config.paths import resolve_project_path
from src.config.settings.base_settings import AppBaseSettings


class ParsedArtifactStoreSettings(AppBaseSettings):
    enabled: bool = Field(
        default=True,
        alias="PARSED_ARTIFACT_STORE_ENABLED",
    )

    cache_dir: str = Field(
        default="data/artifacts/parsed_documents",
        alias="PARSED_ARTIFACT_STORE_DIR",
    )

    @property
    def cache_path(self) -> Path:
        return resolve_project_path(self.cache_dir)

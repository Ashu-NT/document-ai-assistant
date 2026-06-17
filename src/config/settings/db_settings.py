from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from src.config.paths import resolve_project_path


class DatabaseSettings(BaseSettings):
    database_provider: str = Field(alias="DATABASE_PROVIDER")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    database_file: str = Field(alias="DATABASE_FILE")

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def database_path(self) -> Path:
        return resolve_project_path(self.database_file)

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        if self.database_provider == "sqlite":
            return f"sqlite:///{self.database_path.as_posix()}"

        raise ValueError(
            f"Unsupported database provider without DATABASE_URL: {self.database_provider}"
        )

    def ensure_database_directory(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
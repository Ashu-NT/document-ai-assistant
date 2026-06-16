from pydantic import Field
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):

    log_level: str = Field(alias="LOG_LEVEL")

    log_file: str = Field(alias="LOG_FILE")

    log_rotation_size_mb: int = Field(
        default=10,
        alias="LOG_ROTATION_SIZE_MB",
    )

    log_backup_count: int = Field(
        default=5,
        alias="LOG_BACKUP_COUNT",
    )

    log_console_enabled: bool = Field(
        default=True,
        alias="LOG_CONSOLE_ENABLED",
    )

    class Config:
        env_file = ".env"
        extra = "ignore"
        
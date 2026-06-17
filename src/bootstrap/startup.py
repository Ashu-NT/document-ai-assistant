from src.config.settings import (
    database_settings,
    qdrant_settings,
    storage_settings,
)


def bootstrap_application() -> None:
    """
    Prepare application runtime dependencies.

    This should be called once at application startup before:
    - database access
    - logging setup
    - file parsing
    - Qdrant local mode
    """

    storage_settings.ensure_directories()
    database_settings.ensure_database_directory()
    qdrant_settings.ensure_storage_directory()
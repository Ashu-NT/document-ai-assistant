import os

from src.config.logging import configure_logging
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

    # Docling/HuggingFace Hub otherwise attempts a network round-trip on every
    # conversion to check for model updates, even when the model is already
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

    configure_logging()
    storage_settings.ensure_directories()
    database_settings.ensure_database_directory()
    qdrant_settings.ensure_storage_directory()
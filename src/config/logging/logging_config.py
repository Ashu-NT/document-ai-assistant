import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config.settings import logging_settings


def configure_logging() -> None:

    log_path = Path(logging_settings.log_file)

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    handlers = []

    file_handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=logging_settings.log_rotation_size_mb
        * 1024
        * 1024,
        backupCount=logging_settings.log_backup_count,
        encoding="utf-8",
    )

    handlers.append(file_handler)

    if logging_settings.log_console_enabled:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=getattr(
            logging,
            logging_settings.log_level.upper(),
        ),
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=handlers,
    )
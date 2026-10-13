from __future__ import annotations

from dataclasses import dataclass

from src.config.settings import ingestion_settings

_BYTES_PER_MEGABYTE = 1024 * 1024


@dataclass(frozen=True)
class IngestionInputLimits:
    max_file_size_bytes: int
    max_pdf_pages: int
    parse_timeout_seconds: int


def resolve_ingestion_input_limits() -> IngestionInputLimits:
    return IngestionInputLimits(
        max_file_size_bytes=(
            ingestion_settings.max_file_size_mb * _BYTES_PER_MEGABYTE
        ),
        max_pdf_pages=ingestion_settings.max_pdf_pages,
        parse_timeout_seconds=ingestion_settings.parse_timeout_seconds,
    )

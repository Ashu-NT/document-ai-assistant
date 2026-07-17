from __future__ import annotations

from dataclasses import dataclass

from src.config.settings import ingestion_settings


@dataclass(frozen=True)
class ParsingChunkingSettings:
    max_chunk_tokens: int
    chunk_overlap: int
    min_section_text_length: int


def resolve_parsing_chunking_settings() -> ParsingChunkingSettings:
    return ParsingChunkingSettings(
        max_chunk_tokens=ingestion_settings.max_chunk_tokens,
        chunk_overlap=ingestion_settings.chunk_overlap,
        min_section_text_length=ingestion_settings.min_section_text_length,
    )

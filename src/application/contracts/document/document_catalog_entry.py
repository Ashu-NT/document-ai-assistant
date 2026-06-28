from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class DocumentCatalogEntry:
    document_id: str
    title: str | None
    file_name: str
    file_path: str
    document_type: str
    language: str | None
    page_count: int | None
    chunk_count: int
    section_count: int
    identifier_count: int
    table_count: int
    picture_count: int
    created_at: datetime | None

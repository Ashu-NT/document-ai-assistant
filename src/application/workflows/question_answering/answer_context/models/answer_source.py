from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AnswerSource:
    source_number: int
    chunk_id: str
    chunk_name: str | None = None
    chunk_type: str | None = None
    document_id: str | None = None
    document_title: str | None = None
    section_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    score: float | None = None
    content: str = ""
    table_rows: list[list[str]] | None = None

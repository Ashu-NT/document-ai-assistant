from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptSourceView:
    source_number: int
    chunk_id: str
    chunk_name: str | None = None
    chunk_type: str | None = None
    document_id: str | None = None
    document_title: str = "Current document"
    section_path: str = "N/A"
    page_start: int | None = None
    page_end: int | None = None
    score: float | None = None
    content: str = ""
    table_rows: list[list[str]] | None = None
    table_shape: str | None = None
    table_structure_quality: float | None = None
    table_header_paths: list[list[str]] = field(default_factory=list)
    table_axis_summary: dict[str, str] = field(default_factory=dict)
    retrieval_source: str | None = None
    section_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    identifier_values: list[str] = field(default_factory=list)
    collapsed_chunk_ids: list[str] = field(default_factory=list)

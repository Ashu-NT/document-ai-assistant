from __future__ import annotations

from dataclasses import dataclass, field

from src.application.prompts.answer_generation.prompt_context.models.prompt_table_row_view import (
    PromptTableRowView,
)


@dataclass(slots=True, frozen=True)
class PromptTableView:
    table_id: str
    table_type: str
    source_number: int
    chunk_id: str
    chunk_name: str | None = None
    chunk_type: str | None = None
    document_title: str = "Current document"
    section_path: str = "N/A"
    page_start: int | None = None
    page_end: int | None = None
    retrieval_source: str | None = None
    table_shape: str | None = None
    table_category: str | None = None
    table_structure_quality: float | None = None
    header_paths: list[list[str]] = field(default_factory=list)
    axis_summary: dict[str, str] = field(default_factory=dict)
    headers: list[str] = field(default_factory=list)
    rows: list[PromptTableRowView] = field(default_factory=list)

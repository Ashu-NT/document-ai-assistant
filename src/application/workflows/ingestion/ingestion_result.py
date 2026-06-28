from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.workflows.ingestion.ingestion_stage import IngestionStage
from src.application.workflows.ingestion.ingestion_status import IngestionStatus


@dataclass(slots=True)
class IngestionResult:
    status: IngestionStatus
    ingestion_run_id: str | None = None
    document_id: str | None = None
    title: str | None = None
    file_name: str | None = None
    document_type: str | None = None
    page_count: int | None = None
    section_count: int | None = None
    element_count: int | None = None
    chunk_count: int | None = None
    table_count: int | None = None
    picture_count: int | None = None
    identifier_count: int | None = None
    generated_question_count: int | None = None
    vector_count: int | None = None
    duplicate_of_document_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    current_stage: IngestionStage | None = None
    correlation_id: str | None = None

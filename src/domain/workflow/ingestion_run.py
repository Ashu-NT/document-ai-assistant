from dataclasses import dataclass, field
from datetime import datetime

from src.domain.common import AuditMetadata, IngestionStatus


@dataclass(slots=True)
class IngestionRun:
    run_id: str

    document_id: str | None = None
    file_path: str | None = None
    file_hash: str | None = None
    content_hash: str | None = None

    status: IngestionStatus = IngestionStatus.PENDING

    started_at: datetime | None = None
    finished_at: datetime | None = None

    error_message: str | None = None

    parser_name: str | None = None
    parser_version: str | None = None
    embedding_model: str | None = None
    classification_model: str | None = None
    question_generation_model: str | None = None
    extraction_model: str | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def mark_running(self, started_at: datetime) -> None:
        self.status = IngestionStatus.RUNNING
        self.started_at = started_at

    def mark_success(self, finished_at: datetime) -> None:
        self.status = IngestionStatus.SUCCESS
        self.finished_at = finished_at
        self.error_message = None

    def mark_failed(self, finished_at: datetime, error_message: str) -> None:
        self.status = IngestionStatus.FAILED
        self.finished_at = finished_at
        self.error_message = error_message

    def mark_file_duplicate(self, finished_at: datetime) -> None:
        self.status = IngestionStatus.SKIPPED_FILE_DUPLICATE
        self.finished_at = finished_at

    def mark_content_duplicate(self, finished_at: datetime) -> None:
        self.status = IngestionStatus.SKIPPED_CONTENT_DUPLICATE
        self.finished_at = finished_at
from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, SourceLocation
from src.domain.extraction.semantic_source_metadata import SemanticSourceMetadata


@dataclass(slots=True)
class MaintenanceTask:
    task_id: str
    document_id: str

    title: str
    description: str | None = None
    interval: str | None = None

    component_name: str | None = None
    equipment_id: str | None = None

    source_chunk_id: str | None = None
    source: SourceLocation = field(default_factory=SourceLocation)
    source_metadata: SemanticSourceMetadata | None = None

    requires_human_review: bool = True
    confidence_score: float | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def is_complete(self) -> bool:
        return bool(self.title and self.interval)
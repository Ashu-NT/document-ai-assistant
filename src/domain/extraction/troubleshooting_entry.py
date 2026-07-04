from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, SourceLocation
from src.domain.extraction.semantic_source_metadata import SemanticSourceMetadata


@dataclass(slots=True)
class TroubleshootingEntry:
    troubleshooting_id: str
    document_id: str

    symptom: str
    cause: str | None = None
    remedy: str | None = None
    component_name: str | None = None
    equipment_id: str | None = None

    source_chunk_id: str | None = None
    source: SourceLocation = field(default_factory=SourceLocation)
    source_metadata: SemanticSourceMetadata | None = None

    confidence_score: float | None = None
    requires_human_review: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)

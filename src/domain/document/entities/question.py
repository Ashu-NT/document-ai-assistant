from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, ModelProcessingMetadata


@dataclass(slots=True)
class GeneratedQuestion:
    question_id: str
    document_id: str
    chunk_id: str

    question: str

    is_active: bool = True

    processing_metadata: ModelProcessingMetadata | None = None
    audit: AuditMetadata = field(default_factory=AuditMetadata)
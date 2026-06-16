from dataclasses import dataclass, field

from src.domain.common import AuditMetadata


@dataclass(slots=True)
class SemanticMemoryReference:
    reference_id: str

    source_id: str
    source_type: str

    vector_id: str | None = None
    collection_name: str | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)
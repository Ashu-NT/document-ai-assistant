from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, ChunkType
from src.domain.classification.classification_result import ClassificationResult


@dataclass(slots=True)
class ChunkClassification:
    chunk_id: str
    document_id: str
    chunk_type: ChunkType

    result: ClassificationResult | None = None
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def is_unknown(self) -> bool:
        return self.chunk_type == ChunkType.UNKNOWN
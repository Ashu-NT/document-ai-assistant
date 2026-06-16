from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, DocumentType
from src.domain.classification.classification_result import ClassificationResult


@dataclass(slots=True)
class DocumentClassification:
    document_id: str
    document_type: DocumentType

    result: ClassificationResult | None = None
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def is_unknown(self) -> bool:
        return self.document_type == DocumentType.UNKNOWN
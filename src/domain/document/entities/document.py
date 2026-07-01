from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, DocumentType
from src.domain.document.value_objects import DocumentHashes, DocumentStatistics


@dataclass(slots=True)
class Document:
    document_id: str
    file_name: str
    file_path: str

    hashes: DocumentHashes

    title: str | None = None
    document_type: DocumentType = DocumentType.UNKNOWN
    language: str | None = None
    source_name: str | None = None

    statistics: DocumentStatistics = field(default_factory=DocumentStatistics)
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def is_classified(self) -> bool:
        return self.document_type != DocumentType.UNKNOWN
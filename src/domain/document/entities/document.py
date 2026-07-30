from dataclasses import dataclass, field
from typing import Any

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
    parser_version: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)
    statistics: DocumentStatistics = field(default_factory=DocumentStatistics)
    audit: AuditMetadata = field(default_factory=AuditMetadata)

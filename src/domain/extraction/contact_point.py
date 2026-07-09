from dataclasses import dataclass, field
from enum import StrEnum

from src.domain.common import AuditMetadata, SourceLocation
from src.domain.extraction.semantic_relationship import SemanticEntityType
from src.domain.extraction.semantic_source_metadata import SemanticSourceMetadata


class ContactPointType(StrEnum):
    PHONE_NUMBER = "phone_number"
    FAX_NUMBER = "fax_number"
    EMAIL_ADDRESS = "email_address"
    URL = "url"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class ContactPoint:
    contact_point_id: str
    document_id: str

    contact_type: ContactPointType
    value: str
    label: str | None = None
    owner_name: str | None = None
    owner_entity_type: SemanticEntityType | None = None

    source_chunk_id: str | None = None
    source: SourceLocation = field(default_factory=SourceLocation)
    source_metadata: SemanticSourceMetadata | None = None

    confidence_score: float | None = None
    requires_human_review: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)

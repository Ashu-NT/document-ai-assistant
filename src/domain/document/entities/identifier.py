from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, IdentifierType, normalize_identifier


@dataclass(slots=True)
class Identifier:
    identifier_id: str
    document_id: str

    raw_value: str
    identifier_type: IdentifierType = IdentifierType.UNKNOWN

    chunk_id: str | None = None
    element_id: str | None = None

    normalized_value: str | None = None
    confidence_score: float | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def __post_init__(self) -> None:
        if self.normalized_value is None:
            self.normalized_value = normalize_identifier(self.raw_value)
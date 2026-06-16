from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, SourceLocation


@dataclass(slots=True)
class SparePart:
    spare_part_id: str
    document_id: str

    part_number: str | None = None
    description: str | None = None
    quantity: str | None = None

    component_name: str | None = None
    manufacturer_name: str | None = None

    source_chunk_id: str | None = None
    source: SourceLocation = field(default_factory=SourceLocation)

    requires_human_review: bool = True
    confidence_score: float | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_part_number(self) -> bool:
        return bool(self.part_number and self.part_number.strip())
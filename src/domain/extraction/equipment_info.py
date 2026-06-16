from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, SourceLocation


@dataclass(slots=True)
class EquipmentInfo:
    equipment_id: str
    document_id: str

    name: str | None = None
    model_number: str | None = None
    serial_number: str | None = None
    manufacturer_name: str | None = None

    source_chunk_id: str | None = None
    source: SourceLocation = field(default_factory=SourceLocation)

    confidence_score: float | None = None
    requires_human_review: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_identity(self) -> bool:
        return bool(self.name or self.model_number or self.serial_number)
from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, SourceLocation


@dataclass(slots=True)
class DocumentSection:
    section_id: str
    document_id: str

    title: str
    level: int = 1
    parent_section_id: str | None = None
    section_path: list[str] = field(default_factory=list)

    source: SourceLocation = field(default_factory=SourceLocation)

    element_ids: list[str] = field(default_factory=list)

    sequence_number: int | None = None
    reading_order_start: int | None = None
    reading_order_end: int | None = None

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def path_text(self) -> str:
        return " > ".join(self.section_path) if self.section_path else self.title
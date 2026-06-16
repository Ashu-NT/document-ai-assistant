from dataclasses import dataclass, field

from src.domain.common import (
    AuditMetadata,
    ElementType,
    ParserMetadata,
    SourceLocation,
)


@dataclass(slots=True)
class CanonicalElement:
    element_id: str
    document_id: str
    element_type: ElementType

    text: str | None = None

    parent_section_id: str | None = None
    reading_order: int | None = None

    source: SourceLocation = field(default_factory=SourceLocation)

    table_id: str | None = None
    picture_id: str | None = None

    parser_metadata: ParserMetadata | None = None
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_text(self) -> bool:
        return bool(self.text and self.text.strip())

    def belongs_to_section(self) -> bool:
        return self.parent_section_id is not None
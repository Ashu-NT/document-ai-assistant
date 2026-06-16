from dataclasses import dataclass, field

from src.domain.common import AuditMetadata, SourceLocation


@dataclass(slots=True)
class Citation:
    citation_id: str

    document_id: str
    chunk_id: str | None = None
    section_id: str | None = None

    document_name: str | None = None
    section_title: str | None = None

    source: SourceLocation = field(default_factory=SourceLocation)

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def display_text(self) -> str:
        parts = []

        if self.document_name:
            parts.append(self.document_name)

        if self.section_title:
            parts.append(f"section: {self.section_title}")

        if self.source.page_start is not None:
            parts.append(f"page: {self.source.page_start}")

        return ", ".join(parts)
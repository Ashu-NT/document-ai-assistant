from dataclasses import dataclass, field

from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import AuditMetadata


@dataclass(slots=True)
class TableAsset:
    table_id: str
    document_id: str

    markdown: str

    parent_section_id: str | None = None

    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_content(self) -> bool:
        return bool(self.markdown and self.markdown.strip())

    def to_embedding_text(self) -> str:
        parts = []

        if self.metadata.caption:
            parts.append(f"Table Caption: {self.metadata.caption}")

        parts.append(self.markdown)

        return "\n".join(parts)

from dataclasses import dataclass, field

from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.common import AuditMetadata


@dataclass(slots=True)
class PictureAsset:
    picture_id: str
    document_id: str

    parent_section_id: str | None = None

    image_path: str | None = None
    ocr_text: str | None = None
    ocr_confidence: float | None = None

    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_image_file(self) -> bool:
        return bool(self.image_path)

    def has_ocr_text(self) -> bool:
        return bool(self.ocr_text and self.ocr_text.strip())

    def to_embedding_text(self) -> str:
        parts = []

        if self.metadata.caption:
            parts.append(f"Figure Caption: {self.metadata.caption}")

        if self.metadata.nearby_text:
            parts.append(f"Nearby Text: {self.metadata.nearby_text}")

        if self.ocr_text:
            parts.append(f"OCR Text: {self.ocr_text}")

        return "\n".join(parts)
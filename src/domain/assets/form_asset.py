from dataclasses import dataclass, field

from src.domain.assets.asset_metadata import AssetMetadata
from src.domain.assets.form_field import FormField
from src.domain.common import AuditMetadata


@dataclass(slots=True)
class FormAsset:
    form_id: str
    document_id: str

    parent_section_id: str | None = None

    fields: list[FormField] = field(default_factory=list)

    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def has_fields(self) -> bool:
        return bool(self.fields)

    def to_embedding_text(self) -> str:
        parts = []

        if self.metadata.caption:
            parts.append(f"Form Caption: {self.metadata.caption}")

        if self.metadata.nearby_text:
            parts.append(f"Nearby Text: {self.metadata.nearby_text}")

        for form_field in self.fields:
            if form_field.key_text and form_field.value_text:
                parts.append(f"{form_field.key_text}: {form_field.value_text}")
            elif form_field.key_text:
                parts.append(form_field.key_text)
            elif form_field.value_text:
                parts.append(form_field.value_text)

        return "\n".join(parts)

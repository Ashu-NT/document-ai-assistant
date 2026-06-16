from dataclasses import dataclass, field

from src.domain.common import SourceLocation


@dataclass(slots=True)
class AssetMetadata:
    source: SourceLocation = field(default_factory=SourceLocation)
    caption: str | None = None
    nearby_text: str | None = None

    def has_caption(self) -> bool:
        return bool(self.caption and self.caption.strip())

    def has_nearby_text(self) -> bool:
        return bool(self.nearby_text and self.nearby_text.strip())
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class OCRResult:
    text: str
    provider_name: str
    confidence: float | None = None
    language: str | None = None
    source_image_path: str | None = None
    words: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


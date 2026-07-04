from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.document import DocumentChunk


@dataclass(slots=True)
class ExtractionPromptContext:
    document_id: str
    chunks: list[DocumentChunk] = field(default_factory=list)
    previous_error: str | None = None

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class ResearchEvidence:
    evidence_id: str
    task_id: str
    chunk_id: str
    document_id: str
    document_title: str | None
    section_path: list[str]
    page_start: int | None
    page_end: int | None
    chunk_type: str | None
    score: float | None
    content_excerpt: str
    source_tool: str
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

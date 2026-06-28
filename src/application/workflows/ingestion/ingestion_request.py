from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, kw_only=True)
class IngestionRequest:
    file_path: str
    document_type: str | None = None
    title: str | None = None
    source_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    force: bool = False
    generate_questions: bool | None = None
    enable_ocr: bool | None = None
    run_quality_checks: bool = True
    trace: bool = False
    requested_by: str | None = None
    correlation_id: str | None = None

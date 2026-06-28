from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, kw_only=True)
class ReingestionRequest:
    document_id: str
    force: bool = True
    preserve_document_id: bool = True
    run_quality_checks: bool = True
    requested_by: str | None = None
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

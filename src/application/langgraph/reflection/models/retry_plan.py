from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetryPlan:
    retry_query: str
    document_id: str | None
    top_k: int | None
    reason: str
    preserve_initial_evidence: bool = True

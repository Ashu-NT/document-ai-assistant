from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvidenceQuality:
    approved_chunk_count: int
    rejected_chunk_count: int
    document_ids: list[str]
    page_numbers: list[int]
    has_document_leakage: bool
    has_sufficient_evidence: bool
    score: float
    issues: list[str] = field(default_factory=list)

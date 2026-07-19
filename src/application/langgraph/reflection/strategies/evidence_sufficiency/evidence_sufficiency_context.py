from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.application.langgraph.reflection.decomposition import (
    MultiClauseCoverageResult,
)
from src.application.langgraph.reflection.models import AnswerQuality, EvidenceQuality


@dataclass(slots=True, frozen=True)
class EvidenceSufficiencyContext:
    """Everything an `EvidenceSufficiencyStrategy` needs to judge whether a
    generated answer is sufficiently supported -- bundled so the strategy
    interface doesn't grow a long positional/keyword parameter list as more
    strategies are added."""

    question: str
    answer_text: str
    answer_intent: str | None
    selected_document_id: str | None
    approved_chunks: list[dict[str, Any]]
    rejected_chunks: list[dict[str, Any]]
    evidence_quality: EvidenceQuality
    answer_quality: AnswerQuality
    clause_coverage: MultiClauseCoverageResult | None = None

from __future__ import annotations

from typing import TYPE_CHECKING

from src.application.validation.document_quality.quality_check_result import (
    QualityCheckResult,
)

if TYPE_CHECKING:
    from src.domain.retrieval import RetrievedChunk

_MIN_SCORE_THRESHOLD = 0.1
_MAX_LOW_SCORE_RATIO = 0.5


def check_retrieved_chunk_scores(
    chunks: list[RetrievedChunk],
) -> QualityCheckResult:
    name = "retrieval.low_score_chunks"
    if not chunks:
        return QualityCheckResult.ok(name)
    low_score = [
        c for c in chunks
        if c.score is not None and c.score < _MIN_SCORE_THRESHOLD
    ]
    ratio = len(low_score) / len(chunks)
    if ratio > _MAX_LOW_SCORE_RATIO:
        return QualityCheckResult.warn(
            name,
            f"{ratio:.1%} of retrieved chunks have score < {_MIN_SCORE_THRESHOLD}",
            details={
                "low_score_count": len(low_score),
                "total": len(chunks),
                "threshold": _MIN_SCORE_THRESHOLD,
            },
        )
    return QualityCheckResult.ok(name)


def check_retrieved_chunks_have_content(
    chunks: list[RetrievedChunk],
) -> QualityCheckResult:
    name = "retrieval.empty_chunk_content"
    if not chunks:
        return QualityCheckResult.ok(name)
    empty = [c for c in chunks if not (c.content or "").strip()]
    if empty:
        return QualityCheckResult.warn(
            name,
            f"{len(empty)} retrieved chunk(s) have empty content",
            details={"empty_chunk_ids": [c.chunk_id for c in empty]},
        )
    return QualityCheckResult.ok(name)

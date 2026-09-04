from __future__ import annotations

from dataclasses import dataclass

from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_tie_break import (
    pick_best_candidate,
)
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus
from src.domain.document.entities.chunk import DocumentChunk

_CONFIDENCE_RESOLVED_UNIQUE = 0.9
_CONFIDENCE_RESOLVED_AMBIGUOUS = 0.6
_CONFIDENCE_UNRESOLVED = 0.0


@dataclass(slots=True, frozen=True)
class ResolvedTarget:
    target_chunk_id: str | None
    resolution_status: ChunkCrossReferenceResolutionStatus
    confidence_score: float


class ChunkCrossReferenceResolver:
    """Resolves a detected page reference to the chunk on that page, given
    every chunk of the same document. Kept separate from
    `ChunkCrossReferenceDetector` so tie-break rules are unit-testable
    against a hand-built `chunks` fixture without needing real chunk text."""

    def resolve(
        self,
        *,
        target_page: int,
        chunks: list[DocumentChunk],
    ) -> ResolvedTarget:
        candidates = [
            chunk
            for chunk in chunks
            if chunk.source.page_start is not None
            and chunk.source.page_start
            <= target_page
            <= (chunk.source.page_end or chunk.source.page_start)
        ]

        if not candidates:
            return ResolvedTarget(
                target_chunk_id=None,
                resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
                confidence_score=_CONFIDENCE_UNRESOLVED,
            )

        if len(candidates) == 1:
            return ResolvedTarget(
                target_chunk_id=candidates[0].chunk_id,
                resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
                confidence_score=_CONFIDENCE_RESOLVED_UNIQUE,
            )

        best = self._tie_break(candidates, target_page)
        return ResolvedTarget(
            target_chunk_id=best.chunk_id,
            resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS,
            confidence_score=_CONFIDENCE_RESOLVED_AMBIGUOUS,
        )

    @staticmethod
    def _tie_break(
        candidates: list[DocumentChunk], target_page: int
    ) -> DocumentChunk:
        exact_page_start = [
            chunk for chunk in candidates if chunk.source.page_start == target_page
        ]
        pool = exact_page_start or candidates
        return pick_best_candidate(pool)


__all__ = ["ChunkCrossReferenceResolver", "ResolvedTarget"]

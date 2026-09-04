from __future__ import annotations

from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_asset_number_index import (
    ChunkAssetNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_resolver import (
    ResolvedTarget,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_tie_break import (
    pick_best_candidate,
)
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus


_CONFIDENCE_RESOLVED_UNIQUE = 0.75
_CONFIDENCE_RESOLVED_AMBIGUOUS = 0.5
_CONFIDENCE_RESOLVED_PROXIMITY_FALLBACK = 0.3
_CONFIDENCE_UNRESOLVED = 0.0


class ChunkAssetReferenceResolver:

    def resolve_table(
        self,
        *,
        target_label: str,
        index: ChunkAssetNumberIndex,
        source_page: int | None = None,
    ) -> ResolvedTarget:
        return self._resolve(
            index.table_matches(target_label),
            fallback_chunk=index.nearest_table_chunk(source_page),
        )

    def resolve_figure(
        self,
        *,
        target_label: str,
        index: ChunkAssetNumberIndex,
        source_page: int | None = None,
    ) -> ResolvedTarget:
        return self._resolve(
            index.figure_matches(target_label),
            fallback_chunk=index.nearest_figure_chunk(source_page),
        )

    @staticmethod
    def _resolve(candidates, *, fallback_chunk=None) -> ResolvedTarget:
        if not candidates:
            if fallback_chunk is not None:
                return ResolvedTarget(
                    target_chunk_id=fallback_chunk.chunk_id,
                    resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS,
                    confidence_score=_CONFIDENCE_RESOLVED_PROXIMITY_FALLBACK,
                )
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

        best = pick_best_candidate(candidates)
        return ResolvedTarget(
            target_chunk_id=best.chunk_id,
            resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS,
            confidence_score=_CONFIDENCE_RESOLVED_AMBIGUOUS,
        )


__all__ = ["ChunkAssetReferenceResolver"]

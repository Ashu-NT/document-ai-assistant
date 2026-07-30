from __future__ import annotations

from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_asset_number_index import (
    ChunkAssetNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_cross_reference_resolver import (
    ResolvedTarget,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_cross_reference_tie_break import (
    pick_best_candidate,
)
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus

# Lower than the page-based resolver's equivalents (0.9/0.6): resolution
# depends on the source document having numbered its table/figure captions
# in the first place, an assumption that cannot be corpus-verified across
# arbitrary shipyard documents the way page numbers can.
_CONFIDENCE_RESOLVED_UNIQUE = 0.75
_CONFIDENCE_RESOLVED_AMBIGUOUS = 0.5
# Weaker still: no caption number matched at all, so this falls back to
# "the nearest table/figure on an adjacent page" rather than an actual
# label match -- a guess, not a resolution, hence the low confidence.
_CONFIDENCE_RESOLVED_PROXIMITY_FALLBACK = 0.3
_CONFIDENCE_UNRESOLVED = 0.0


class ChunkAssetReferenceResolver:
    """Resolves a detected table/figure reference ("see Table 3") to a chunk
    containing that asset, using the leading number already extracted from
    the asset's caption by `ChunkAssetNumberIndex`. Unlike section
    resolution, there is no descendant/hierarchical fallback -- a table/
    figure number is a flat label, not a nested path. When no caption
    numbering matches at all (uncaptioned or inconsistently-numbered
    documents), falls back to the nearest table/figure on an adjacent page
    rather than leaving the reference unresolved outright."""

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

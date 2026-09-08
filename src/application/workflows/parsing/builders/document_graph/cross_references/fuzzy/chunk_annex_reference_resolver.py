from __future__ import annotations

from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_annex_number_index import (
    ChunkAnnexNumberIndex,
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
_CONFIDENCE_UNRESOLVED = 0.0


class ChunkAnnexReferenceResolver:
    """Resolves a detected annex/appendix reference ("Annex 2", "Appendix
    B") against chunk content mentioning that label. Unresolved is an
    expected, non-error outcome when no chunk mentions that annex/appendix
    label -- same philosophy as an uncaptioned table/figure."""

    def resolve(
        self,
        *,
        target_label: str,
        index: ChunkAnnexNumberIndex,
    ) -> ResolvedTarget:
        candidates = index.matches(target_label)
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

        best = pick_best_candidate(candidates)
        return ResolvedTarget(
            target_chunk_id=best.chunk_id,
            resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS,
            confidence_score=_CONFIDENCE_RESOLVED_AMBIGUOUS,
        )


__all__ = ["ChunkAnnexReferenceResolver"]

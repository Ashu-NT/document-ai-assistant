from __future__ import annotations

from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_resolver import (
    ResolvedTarget,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_tie_break import (
    pick_best_candidate,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_section_number_index import (
    ChunkSectionNumberIndex,
)
from src.domain.document.entities import ChunkCrossReferenceResolutionStatus


_CONFIDENCE_RESOLVED_UNIQUE = 0.85
_CONFIDENCE_RESOLVED_AMBIGUOUS = 0.55
_CONFIDENCE_RESOLVED_DESCENDANT = 0.5
_CONFIDENCE_UNRESOLVED = 0.0


class ChunkSectionReferenceResolver:
    """Resolves a detected section/chapter-number reference ("chap. 8.9")
    to a chunk under that numbered section, using the numeric prefix
    already present in `chunk.section_path` titles (e.g. "8.9 Lubrication
    oil"). Falls back to the nearest numbered descendant subsection when the
    referenced section itself has no directly-chunked content."""

    def resolve(
        self,
        *,
        target_section_label: str,
        index: ChunkSectionNumberIndex,
    ) -> ResolvedTarget:
        exact_candidates = index.exact_match(target_section_label)
        if exact_candidates:
            if len(exact_candidates) == 1:
                return ResolvedTarget(
                    target_chunk_id=exact_candidates[0].chunk_id,
                    resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE,
                    confidence_score=_CONFIDENCE_RESOLVED_UNIQUE,
                )
            best = pick_best_candidate(exact_candidates)
            return ResolvedTarget(
                target_chunk_id=best.chunk_id,
                resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS,
                confidence_score=_CONFIDENCE_RESOLVED_AMBIGUOUS,
            )

        descendant_candidates = index.descendant_matches(target_section_label)
        if descendant_candidates:
            best = pick_best_candidate(descendant_candidates)
            return ResolvedTarget(
                target_chunk_id=best.chunk_id,
                resolution_status=ChunkCrossReferenceResolutionStatus.RESOLVED_AMBIGUOUS,
                confidence_score=_CONFIDENCE_RESOLVED_DESCENDANT,
            )

        return ResolvedTarget(
            target_chunk_id=None,
            resolution_status=ChunkCrossReferenceResolutionStatus.UNRESOLVED,
            confidence_score=_CONFIDENCE_UNRESOLVED,
        )


__all__ = ["ChunkSectionReferenceResolver"]

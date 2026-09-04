import logging
from dataclasses import dataclass, field

from src.application.contracts.pdf_links import PdfLinkExtractionResult
from src.application.workflows.parsing.builders.document_graph.cross_references.pdf_link.chunk_page_index import (
    ChunkPageIndex,
)
from src.config.logging import get_logger
from src.domain.document import DocumentGraph
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
    PdfLinkProvenance,
)
from src.shared.ids import IdGenerator, IdPrefix
from src.shared.observability.stage_logger import time_stage

_logger = get_logger(__name__)

# Legacy compatibility value, not a calibrated probability. Copied verbatim
# from ChunkCrossReferenceResolver's own _CONFIDENCE_RESOLVED_UNIQUE purely
# so PDF_LINK_REFERENCE rows sit on the same numeric scale as every other
# reference type already in chunk_cross_references - no corpus-derived
# confidence number exists yet for either resolver.
_CONFIDENCE_RESOLVED_UNIQUE = 0.9
_MATCHED_TEXT = "pdf_link_annotation"


@dataclass(slots=True, frozen=True)
class PdfLinkLinkingDiagnostics:
    ambiguous_count: int = 0
    unresolved_count: int = 0
    self_reference_count: int = 0
    duplicate_count: int = 0


@dataclass(slots=True, frozen=True)
class PdfLinkLinkingResult:
    references: list[ChunkCrossReference] = field(default_factory=list)
    diagnostics: PdfLinkLinkingDiagnostics = field(
        default_factory=PdfLinkLinkingDiagnostics
    )


class PdfLinkCrossReferenceLinker:
    """Resolves each extracted PdfLinkAnnotation's source/dest page to a
    unique chunk via ChunkPageIndex.

    Pure with respect to `graph` - mirrors the existing fuzzy
    ChunkCrossReferenceLinker's convention exactly: only ever reads
    `graph.chunks`, never calls `graph.add_cross_reference` itself. The
    caller (CrossReferencePipeline / DocumentGraphBuilder) owns the add.

    Resolution rules per annotation: 0 candidate chunks on either side ->
    unresolved (skip, count); 2+ candidates on either side -> ambiguous
    (skip, count, no tie-break); same chunk on both sides -> self-reference
    (skip, count); a duplicate (source_chunk_id, target_chunk_id) pair
    already produced this pass -> skip, count. Only an exactly-one-candidate
    match on both sides produces a reference.
    """

    def __init__(self, *, id_generator: IdGenerator) -> None:
        self.id_generator = id_generator

    def link(
        self,
        graph: DocumentGraph,
        extraction_result: PdfLinkExtractionResult,
    ) -> PdfLinkLinkingResult:
        with time_stage(
            _logger,
            "pdf_native_cross_reference_linker",
            document_id=graph.document.document_id,
            success_level=logging.DEBUG,
        ) as scope:
            result = self._link(graph, extraction_result)
            scope.counts.update(
                {
                    "annotations": len(extraction_result.annotations),
                    "resolved": len(result.references),
                    "ambiguous": result.diagnostics.ambiguous_count,
                    "unresolved": result.diagnostics.unresolved_count,
                    "self_reference": result.diagnostics.self_reference_count,
                    "duplicate": result.diagnostics.duplicate_count,
                }
            )
        return result

    def _link(
        self,
        graph: DocumentGraph,
        extraction_result: PdfLinkExtractionResult,
    ) -> PdfLinkLinkingResult:
        page_index = ChunkPageIndex(list(graph.chunks.values()))

        references: list[ChunkCrossReference] = []
        seen_pairs: set[tuple[str, str]] = set()
        ambiguous_count = 0
        unresolved_count = 0
        self_reference_count = 0
        duplicate_count = 0

        for annotation in extraction_result.annotations:
            source_candidates = page_index.chunks_for_page(annotation.source_page)
            dest_candidates = page_index.chunks_for_page(annotation.dest_page)

            if not source_candidates or not dest_candidates:
                unresolved_count += 1
                continue
            if len(source_candidates) > 1 or len(dest_candidates) > 1:
                ambiguous_count += 1
                continue

            source_chunk = source_candidates[0]
            dest_chunk = dest_candidates[0]

            if source_chunk.chunk_id == dest_chunk.chunk_id:
                self_reference_count += 1
                continue

            pair = (source_chunk.chunk_id, dest_chunk.chunk_id)
            if pair in seen_pairs:
                duplicate_count += 1
                continue
            seen_pairs.add(pair)

            references.append(
                ChunkCrossReference(
                    cross_reference_id=self.id_generator.new_id(
                        IdPrefix.CROSS_REFERENCE
                    ),
                    document_id=graph.document.document_id,
                    source_chunk_id=source_chunk.chunk_id,
                    reference_type=ChunkCrossReferenceType.PDF_LINK_REFERENCE,
                    matched_text=_MATCHED_TEXT,
                    target_page=annotation.dest_page,
                    target_chunk_id=dest_chunk.chunk_id,
                    resolution_status=(
                        ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE
                    ),
                    confidence_score=_CONFIDENCE_RESOLVED_UNIQUE,
                    link_provenance=PdfLinkProvenance(
                        source_page=annotation.source_page,
                        link_kind=annotation.link_kind,
                        source_rect=annotation.source_rect,
                        rect_coordinate_origin=annotation.rect_coordinate_origin,
                        source_page_size=annotation.source_page_size,
                        source_page_rotation_degrees=(
                            annotation.source_page_rotation_degrees
                        ),
                        source_page_label=annotation.source_page_label,
                        dest_page_label=annotation.dest_page_label,
                    ),
                )
            )

        return PdfLinkLinkingResult(
            references=references,
            diagnostics=PdfLinkLinkingDiagnostics(
                ambiguous_count=ambiguous_count,
                unresolved_count=unresolved_count,
                self_reference_count=self_reference_count,
                duplicate_count=duplicate_count,
            ),
        )


__all__ = [
    "PdfLinkCrossReferenceLinker",
    "PdfLinkLinkingDiagnostics",
    "PdfLinkLinkingResult",
]

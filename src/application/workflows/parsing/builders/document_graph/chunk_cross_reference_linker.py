from __future__ import annotations

from src.application.workflows.parsing.builders.document_graph.chunk_cross_reference_detector import (
    ChunkCrossReferenceDetector,
)
from src.application.workflows.parsing.builders.document_graph.chunk_cross_reference_resolver import (
    ChunkCrossReferenceResolver,
)
from src.application.workflows.parsing.builders.document_graph.chunk_section_number_index import (
    ChunkSectionNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.chunk_section_reference_resolver import (
    ChunkSectionReferenceResolver,
)
from src.domain.document import DocumentGraph
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceType,
)
from src.shared.ids import IdGenerator, IdPrefix


class ChunkCrossReferenceLinker:
    """Detects and resolves same-document inline cross-references
    ("(-> Page 1062)", "see chapter 8.9") across every chunk of a document,
    producing `ChunkCrossReference` rows. Runs against `graph.chunks`, which
    must already be fully populated (final content/page/chunk_type) -- see
    `DocumentGraphBuilder.build()`, where this is called right after
    `GraphChunkBuilder.build_chunks` populates the graph, before
    persistence."""

    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        detector: ChunkCrossReferenceDetector | None = None,
        resolver: ChunkCrossReferenceResolver | None = None,
        section_resolver: ChunkSectionReferenceResolver | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.detector = detector or ChunkCrossReferenceDetector()
        self.resolver = resolver or ChunkCrossReferenceResolver()
        self.section_resolver = section_resolver or ChunkSectionReferenceResolver()

    def link(self, graph: DocumentGraph) -> list[ChunkCrossReference]:
        chunks = list(graph.chunks.values())
        section_index = ChunkSectionNumberIndex(chunks)
        cross_references: list[ChunkCrossReference] = []

        for chunk in chunks:
            detection = self.detector.detect(chunk.content)

            for page_reference in detection.page_references:
                resolved = self.resolver.resolve(
                    target_page=page_reference.target_page,
                    chunks=chunks,
                )
                if resolved.target_chunk_id == chunk.chunk_id:
                    continue

                cross_references.append(
                    ChunkCrossReference(
                        cross_reference_id=self.id_generator.new_id(
                            IdPrefix.CROSS_REFERENCE
                        ),
                        document_id=graph.document.document_id,
                        source_chunk_id=chunk.chunk_id,
                        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
                        matched_text=page_reference.matched_text,
                        target_page=page_reference.target_page,
                        target_chunk_id=resolved.target_chunk_id,
                        resolution_status=resolved.resolution_status,
                        confidence_score=resolved.confidence_score,
                    )
                )

            for section_reference in detection.section_references:
                resolved = self.section_resolver.resolve(
                    target_section_label=section_reference.target_section_label,
                    index=section_index,
                )
                if resolved.target_chunk_id == chunk.chunk_id:
                    continue

                cross_references.append(
                    ChunkCrossReference(
                        cross_reference_id=self.id_generator.new_id(
                            IdPrefix.CROSS_REFERENCE
                        ),
                        document_id=graph.document.document_id,
                        source_chunk_id=chunk.chunk_id,
                        reference_type=ChunkCrossReferenceType.SECTION_REFERENCE,
                        matched_text=section_reference.matched_text,
                        target_section_label=section_reference.target_section_label,
                        target_chunk_id=resolved.target_chunk_id,
                        resolution_status=resolved.resolution_status,
                        confidence_score=resolved.confidence_score,
                    )
                )

        return cross_references


__all__ = ["ChunkCrossReferenceLinker"]

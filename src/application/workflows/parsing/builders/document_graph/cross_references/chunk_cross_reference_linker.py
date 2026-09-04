from __future__ import annotations

from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_asset_number_index import (
    ChunkAssetNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_asset_reference_resolver import (
    ChunkAssetReferenceResolver,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_cross_reference_detector import (
    ChunkCrossReferenceDetector,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_cross_reference_resolver import (
    ChunkCrossReferenceResolver,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_section_number_index import (
    ChunkSectionNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.chunk_section_reference_resolver import (
    ChunkSectionReferenceResolver,
)
from src.domain.document import DocumentGraph
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceType,
)
from src.shared.ids import IdGenerator, IdPrefix


class ChunkCrossReferenceLinker:

    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        detector: ChunkCrossReferenceDetector | None = None,
        resolver: ChunkCrossReferenceResolver | None = None,
        section_resolver: ChunkSectionReferenceResolver | None = None,
        asset_resolver: ChunkAssetReferenceResolver | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.detector = detector or ChunkCrossReferenceDetector()
        self.resolver = resolver or ChunkCrossReferenceResolver()
        self.section_resolver = section_resolver or ChunkSectionReferenceResolver()
        self.asset_resolver = asset_resolver or ChunkAssetReferenceResolver()

    def link(self, graph: DocumentGraph) -> list[ChunkCrossReference]:
        chunks = list(graph.chunks.values())
        section_index = ChunkSectionNumberIndex(chunks)
        asset_index = ChunkAssetNumberIndex(
            chunks=chunks,
            tables=graph.tables,
            pictures=graph.pictures,
        )
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

            source_page = chunk.source.page_start or chunk.source.page_end

            for table_reference in detection.table_references:
                resolved = self.asset_resolver.resolve_table(
                    target_label=table_reference.target_asset_label,
                    index=asset_index,
                    source_page=source_page,
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
                        reference_type=ChunkCrossReferenceType.TABLE_REFERENCE,
                        matched_text=table_reference.matched_text,
                        target_asset_label=table_reference.target_asset_label,
                        target_chunk_id=resolved.target_chunk_id,
                        resolution_status=resolved.resolution_status,
                        confidence_score=resolved.confidence_score,
                    )
                )

            for figure_reference in detection.figure_references:
                resolved = self.asset_resolver.resolve_figure(
                    target_label=figure_reference.target_asset_label,
                    index=asset_index,
                    source_page=source_page,
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
                        reference_type=ChunkCrossReferenceType.FIGURE_REFERENCE,
                        matched_text=figure_reference.matched_text,
                        target_asset_label=figure_reference.target_asset_label,
                        target_chunk_id=resolved.target_chunk_id,
                        resolution_status=resolved.resolution_status,
                        confidence_score=resolved.confidence_score,
                    )
                )

        return cross_references


__all__ = ["ChunkCrossReferenceLinker"]

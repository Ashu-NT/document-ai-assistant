from __future__ import annotations

import logging

from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_annex_number_index import (
    ChunkAnnexNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_annex_reference_resolver import (
    ChunkAnnexReferenceResolver,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_asset_number_index import (
    ChunkAssetNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_asset_reference_resolver import (
    ChunkAssetReferenceResolver,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_context_qualifier import (
    ChunkCrossReferenceContextQualifier,
    extract_local_reference_context,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_detector import (
    ChunkCrossReferenceDetector,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_cross_reference_resolver import (
    ChunkCrossReferenceResolver,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_section_number_index import (
    ChunkSectionNumberIndex,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.chunk_section_reference_resolver import (
    ChunkSectionReferenceResolver,
)
from src.application.workflows.parsing.builders.document_graph.cross_references.fuzzy.cross_reference_qualification import (
    CrossReferenceScope,
)
from src.config.logging import get_logger
from src.domain.document import DocumentGraph
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceType,
)
from src.shared.ids import IdGenerator, IdPrefix
from src.shared.observability.stage_logger import time_stage

_logger = get_logger(__name__)


class ChunkCrossReferenceLinker:

    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        detector: ChunkCrossReferenceDetector | None = None,
        resolver: ChunkCrossReferenceResolver | None = None,
        section_resolver: ChunkSectionReferenceResolver | None = None,
        asset_resolver: ChunkAssetReferenceResolver | None = None,
        annex_resolver: ChunkAnnexReferenceResolver | None = None,
        context_qualifier: ChunkCrossReferenceContextQualifier | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.detector = detector or ChunkCrossReferenceDetector()
        self.resolver = resolver or ChunkCrossReferenceResolver()
        self.section_resolver = section_resolver or ChunkSectionReferenceResolver()
        self.asset_resolver = asset_resolver or ChunkAssetReferenceResolver()
        self.annex_resolver = annex_resolver or ChunkAnnexReferenceResolver()
        self.context_qualifier = context_qualifier or ChunkCrossReferenceContextQualifier()

    def link(self, graph: DocumentGraph) -> list[ChunkCrossReference]:
        with time_stage(
            _logger,
            "fuzzy_cross_reference_linker",
            document_id=graph.document.document_id,
            success_level=logging.DEBUG,
        ) as scope:
            cross_references, qualification_counts = self._link(graph)
            counts: dict[str, int] = {}
            for reference in cross_references:
                key = reference.reference_type.value
                counts[key] = counts.get(key, 0) + 1
            scope.counts.update(counts)
            scope.counts.update(qualification_counts)
            scope.counts["total"] = len(cross_references)
        return cross_references

    def _link(
        self, graph: DocumentGraph
    ) -> tuple[list[ChunkCrossReference], dict[str, int]]:
        chunks = list(graph.chunks.values())
        section_index = ChunkSectionNumberIndex(chunks, sections=graph.sections)
        annex_index = ChunkAnnexNumberIndex(chunks)
        asset_index = ChunkAssetNumberIndex(
            chunks=chunks,
            tables=graph.tables,
            pictures=graph.pictures,
        )
        cross_references: list[ChunkCrossReference] = []
        qualification_counts: dict[str, int] = {}

        for chunk in chunks:
            detection = self.detector.detect(chunk.content)

            for section_reference in detection.section_references:
                target_exists = bool(
                    section_index.exact_match(section_reference.target_section_label)
                    or section_index.descendant_matches(
                        section_reference.target_section_label
                    )
                )
                local_context = extract_local_reference_context(
                    chunk.content, section_reference.span
                )
                qualification = self.context_qualifier.qualify_reference(
                    is_explicit_lead_in=section_reference.is_explicit_lead_in,
                    context_text=local_context,
                    target_exists_in_document=target_exists,
                )
                qualification_key = f"section_reference_{qualification.scope.value}"
                qualification_counts[qualification_key] = (
                    qualification_counts.get(qualification_key, 0) + 1
                )
                if qualification.scope != CrossReferenceScope.INTERNAL:
                    continue

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

            for annex_reference in detection.annex_references:
                target_exists = bool(
                    annex_index.matches(annex_reference.target_annex_label)
                )
                local_context = extract_local_reference_context(
                    chunk.content, annex_reference.span
                )
                qualification = self.context_qualifier.qualify_reference(
                    is_explicit_lead_in=annex_reference.is_explicit_lead_in,
                    context_text=local_context,
                    target_exists_in_document=target_exists,
                )
                qualification_key = f"annex_reference_{qualification.scope.value}"
                qualification_counts[qualification_key] = (
                    qualification_counts.get(qualification_key, 0) + 1
                )
                if qualification.scope != CrossReferenceScope.INTERNAL:
                    continue

                resolved = self.annex_resolver.resolve(
                    target_label=annex_reference.target_annex_label,
                    index=annex_index,
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
                        reference_type=ChunkCrossReferenceType.ANNEX_REFERENCE,
                        matched_text=annex_reference.matched_text,
                        target_annex_label=annex_reference.target_annex_label,
                        target_chunk_id=resolved.target_chunk_id,
                        resolution_status=resolved.resolution_status,
                        confidence_score=resolved.confidence_score,
                    )
                )

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

        return cross_references, qualification_counts


__all__ = ["ChunkCrossReferenceLinker"]

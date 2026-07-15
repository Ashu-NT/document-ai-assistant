from src.application.workflows.parsing.builders.document_graph.chunk_statistics_builder import (
    ChunkStatisticsBuilder,
)
from src.application.workflows.parsing.builders.chunking.policies.chunking_profile import (
    ChunkingProfile,
)
from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.application.workflows.parsing.profiling import GraphBuildProfiler
from src.domain.common import SourceLocation
from src.domain.common import DocumentType
from src.domain.document import DocumentChunk, DocumentGraph, DocumentSection
from src.shared.ids import IdGenerator, IdPrefix


class GraphChunkBuilder:
    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        section_chunk_builder: SectionChunkBuilder,
        chunk_statistics_builder: ChunkStatisticsBuilder | None = None,
        profiler: GraphBuildProfiler | None = None,
    ) -> None:
        self.id_generator = id_generator
        self.section_chunk_builder = section_chunk_builder
        self.chunk_statistics_builder = (
            chunk_statistics_builder
            or self._build_default_chunk_statistics_builder(section_chunk_builder)
        )
        self.profiler = profiler or GraphBuildProfiler.disabled()

    def set_profiler(self, profiler: GraphBuildProfiler | None) -> None:
        self.profiler = profiler or GraphBuildProfiler.disabled()
        if hasattr(self.section_chunk_builder, "set_profiler"):
            self.section_chunk_builder.set_profiler(profiler)

    def build_chunks(
        self,
        *,
        graph: DocumentGraph,
        sections: list[DocumentSection],
        document_type_override: DocumentType | None = None,
        chunking_profile_override: ChunkingProfile | None = None,
        page_sizes: dict[int, tuple[float, float]] | None = None,
    ) -> list[DocumentChunk]:
        with self.profiler.measure(
            name="graph_chunk_builder.order_sections",
            input_counts={"sections": len(sections)},
        ) as stage:
            ordered_sections = sorted(
                sections,
                key=lambda value: value.sequence_number or 0,
            )
            stage.output_counts["ordered_sections"] = len(ordered_sections)
        with self.profiler.measure(
            name="graph_chunk_builder.index_section_elements",
            input_counts={"sections": len(ordered_sections)},
        ) as stage:
            section_elements_by_id = {
                section.section_id: graph.get_section_elements(section.section_id)
                for section in ordered_sections
            }
            stage.output_counts["indexed_sections"] = len(section_elements_by_id)
            stage.operations["indexed_elements"] = sum(
                len(elements)
                for elements in section_elements_by_id.values()
            )
        with self.profiler.measure(
            name="graph_chunk_builder.build_payloads",
            input_counts={"sections": len(ordered_sections)},
        ) as stage:
            chunk_payloads = self.section_chunk_builder.build_document_chunk_payloads(
                document_title=graph.document.title,
                document_type=document_type_override or graph.document.document_type,
                chunking_profile_override=chunking_profile_override,
                sections=ordered_sections,
                section_elements_by_id=section_elements_by_id,
                page_sizes=page_sizes,
            )
            stage.output_counts["chunk_payloads"] = len(chunk_payloads)
        chunk_totals_by_section: dict[str, int] = {}
        chunk_indexes_by_section: dict[str, int] = {}

        for chunk_payload in chunk_payloads:
            section_key = chunk_payload.section_id or ""
            chunk_totals_by_section[section_key] = (
                chunk_totals_by_section.get(section_key, 0) + 1
            )

        with self.profiler.measure(
            name="graph_chunk_builder.materialize_chunks",
            input_counts={"chunk_payloads": len(chunk_payloads)},
        ) as stage:
            chunks: list[DocumentChunk] = []
            for sequence_number, chunk_payload in enumerate(chunk_payloads, start=1):
                section_key = chunk_payload.section_id or ""
                chunk_indexes_by_section[section_key] = (
                    chunk_indexes_by_section.get(section_key, 0) + 1
                )
                chunks.append(
                    DocumentChunk(
                        chunk_id=self.id_generator.new_id(IdPrefix.CHUNK),
                        document_id=graph.document.document_id,
                        section_id=chunk_payload.section_id,
                        content=chunk_payload.content,
                        chunk_type=chunk_payload.chunk_type,
                        section_path=list(chunk_payload.section_path),
                        element_ids=list(chunk_payload.element_ids),
                        table_ids=list(chunk_payload.table_ids),
                        picture_ids=list(chunk_payload.picture_ids),
                        logical_table_family_id=chunk_payload.logical_table_family_id,
                        logical_table_family_index=chunk_payload.logical_table_family_index,
                        logical_table_family_total=chunk_payload.logical_table_family_total,
                        logical_table_continuation_role=chunk_payload.logical_table_continuation_role,
                        table_category=chunk_payload.table_category,
                        table_category_confidence=chunk_payload.table_category_confidence,
                        table_row_start=chunk_payload.table_row_start,
                        table_row_end=chunk_payload.table_row_end,
                        table_shape=chunk_payload.table_shape,
                        table_structure_quality=chunk_payload.table_structure_quality,
                        header_paths=list(chunk_payload.header_paths),
                        axis_summary=dict(chunk_payload.axis_summary),
                        source=SourceLocation(
                            page_start=chunk_payload.page_start,
                            page_end=chunk_payload.page_end,
                        ),
                        sequence_number=sequence_number,
                        chunk_index=chunk_indexes_by_section[section_key],
                        chunk_total=chunk_totals_by_section[section_key],
                        embedding_text=chunk_payload.embedding_text,
                        statistics=self.chunk_statistics_builder.build(
                            chunk_payload.content
                        ),
                    )
                )
            stage.output_counts["chunks"] = len(chunks)

        return chunks

    @staticmethod
    def _build_default_chunk_statistics_builder(
        section_chunk_builder: SectionChunkBuilder,
    ) -> ChunkStatisticsBuilder:
        runtime_factory = getattr(section_chunk_builder, "runtime_factory", None)
        if runtime_factory is None:
            return ChunkStatisticsBuilder()

        return ChunkStatisticsBuilder(
            token_counter=getattr(runtime_factory, "token_counter", None),
            token_counter_factory=getattr(runtime_factory, "token_counter_factory", None),
        )

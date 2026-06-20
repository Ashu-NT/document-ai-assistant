from src.application.workflows.parsing.builders.chunking import SectionChunkBuilder
from src.domain.common import SourceLocation
from src.domain.document import DocumentChunk, DocumentGraph, DocumentSection
from src.shared.ids import IdGenerator, IdPrefix


class GraphChunkBuilder:
    def __init__(
        self,
        *,
        id_generator: IdGenerator,
        section_chunk_builder: SectionChunkBuilder,
    ) -> None:
        self.id_generator = id_generator
        self.section_chunk_builder = section_chunk_builder

    def build_chunks(
        self,
        *,
        graph: DocumentGraph,
        sections: list[DocumentSection],
    ) -> list[DocumentChunk]:
        ordered_sections = sorted(
            sections,
            key=lambda value: value.sequence_number or 0,
        )
        section_elements_by_id = {
            section.section_id: graph.get_section_elements(section.section_id)
            for section in ordered_sections
        }
        chunk_payloads = self.section_chunk_builder.build_document_chunk_payloads(
            document_title=graph.document.title,
            sections=ordered_sections,
            section_elements_by_id=section_elements_by_id,
        )
        chunk_totals_by_section: dict[str, int] = {}
        chunk_indexes_by_section: dict[str, int] = {}

        for chunk_payload in chunk_payloads:
            section_key = chunk_payload.section_id or ""
            chunk_totals_by_section[section_key] = (
                chunk_totals_by_section.get(section_key, 0) + 1
            )

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
                    source=SourceLocation(
                        page_start=chunk_payload.page_start,
                        page_end=chunk_payload.page_end,
                    ),
                    sequence_number=sequence_number,
                    chunk_index=chunk_indexes_by_section[section_key],
                    chunk_total=chunk_totals_by_section[section_key],
                    embedding_text=chunk_payload.embedding_text,
                )
            )

        return chunks

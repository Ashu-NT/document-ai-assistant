from src.application.workflows.extraction.context.semantic_extraction_context import (
    SemanticExtractionContext,
)
from src.domain.document import DocumentChunk, DocumentSection


class SemanticExtractionContextBuilder:
    """
    Builds a SemanticExtractionContext for every chunk in a document from
    its full chunk list and DocumentSection map. Chunks are grouped by
    section once so nearby-chunk resolution is a single lookup per chunk
    instead of rescanning the whole document per entity extracted.
    """

    def build_all(
        self,
        *,
        document_id: str,
        chunks: list[DocumentChunk],
        sections: dict[str, DocumentSection] | None = None,
    ) -> dict[str, SemanticExtractionContext]:
        section_lookup = sections or {}
        chunks_by_section, index_by_chunk_id = self._group_by_section(chunks)

        contexts: dict[str, SemanticExtractionContext] = {}
        for chunk in chunks:
            section = (
                section_lookup.get(chunk.section_id) if chunk.section_id else None
            )
            contexts[chunk.chunk_id] = SemanticExtractionContext(
                document_id=document_id,
                chunk=chunk,
                section=section,
                nearby_chunk_ids=self._resolve_nearby_chunk_ids(
                    chunk, chunks_by_section, index_by_chunk_id
                ),
            )
        return contexts

    @staticmethod
    def _group_by_section(
        chunks: list[DocumentChunk],
    ) -> tuple[dict[str, list[DocumentChunk]], dict[str, int]]:
        grouped: dict[str, list[DocumentChunk]] = {}
        for chunk in chunks:
            if not chunk.section_id:
                continue
            grouped.setdefault(chunk.section_id, []).append(chunk)

        # Each chunk's position within its (now-sorted) section list is
        # recorded here as it's computed, so _resolve_nearby_chunk_ids can
        # look it up in O(1) instead of re-scanning the section's chunk
        # list to find "where am I" for every chunk.
        index_by_chunk_id: dict[str, int] = {}
        for section_chunks in grouped.values():
            section_chunks.sort(key=lambda chunk: chunk.chunk_index)
            for index, chunk in enumerate(section_chunks):
                index_by_chunk_id[chunk.chunk_id] = index

        return grouped, index_by_chunk_id

    @staticmethod
    def _resolve_nearby_chunk_ids(
        chunk: DocumentChunk,
        chunks_by_section: dict[str, list[DocumentChunk]],
        index_by_chunk_id: dict[str, int],
    ) -> tuple[str, ...]:
        if not chunk.section_id:
            return ()

        siblings = chunks_by_section.get(chunk.section_id, [])
        index = index_by_chunk_id.get(chunk.chunk_id)
        if index is None:
            return ()

        nearby: list[str] = []
        if index > 0:
            nearby.append(siblings[index - 1].chunk_id)
        if index < len(siblings) - 1:
            nearby.append(siblings[index + 1].chunk_id)
        return tuple(nearby)

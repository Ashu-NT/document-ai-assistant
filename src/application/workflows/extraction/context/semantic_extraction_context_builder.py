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
        chunks_by_section = self._group_by_section(chunks)

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
                    chunk, chunks_by_section
                ),
            )
        return contexts

    @staticmethod
    def _group_by_section(
        chunks: list[DocumentChunk],
    ) -> dict[str, list[DocumentChunk]]:
        grouped: dict[str, list[DocumentChunk]] = {}
        for chunk in chunks:
            if not chunk.section_id:
                continue
            grouped.setdefault(chunk.section_id, []).append(chunk)

        for section_chunks in grouped.values():
            section_chunks.sort(key=lambda chunk: chunk.chunk_index)

        return grouped

    @staticmethod
    def _resolve_nearby_chunk_ids(
        chunk: DocumentChunk,
        chunks_by_section: dict[str, list[DocumentChunk]],
    ) -> tuple[str, ...]:
        if not chunk.section_id:
            return ()

        siblings = chunks_by_section.get(chunk.section_id, [])
        index = next(
            (
                i
                for i, sibling in enumerate(siblings)
                if sibling.chunk_id == chunk.chunk_id
            ),
            None,
        )
        if index is None:
            return ()

        nearby: list[str] = []
        if index > 0:
            nearby.append(siblings[index - 1].chunk_id)
        if index < len(siblings) - 1:
            nearby.append(siblings[index + 1].chunk_id)
        return tuple(nearby)

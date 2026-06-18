from src.domain.document.entities import DocumentChunk


class QdrantPayloadMapper:
    @staticmethod
    def from_chunk(chunk: DocumentChunk) -> dict:
        return {
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "section_id": chunk.section_id,
            "chunk_type": chunk.chunk_type.value,
            "page_start": chunk.source.page_start,
            "page_end": chunk.source.page_end,
        }
from src.application.services.document import DocumentLookupService
from src.domain.retrieval import RetrievedChunk


class RetrievalContextExpander:
    def __init__(
        self,
        document_lookup_service: DocumentLookupService,
        *,
        neighbor_window: int = 1,
    ) -> None:
        self.document_lookup_service = document_lookup_service
        self.neighbor_window = max(0, neighbor_window)

    def expand(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if not chunks or self.neighbor_window <= 0:
            return list(chunks)

        expanded: list[RetrievedChunk] = []
        seen: set[str] = set()
        chunk_cache: dict[str, list] = {}

        for chunk in chunks:
            self._append_chunk(expanded, seen, chunk)

            document_chunks = chunk_cache.get(chunk.document_id)
            if document_chunks is None:
                document_chunks = self.document_lookup_service.list_chunks_by_document(
                    chunk.document_id
                )
                chunk_cache[chunk.document_id] = document_chunks

            chunk_by_id = {
                document_chunk.chunk_id: document_chunk
                for document_chunk in document_chunks
            }
            anchor_document_chunk = chunk_by_id.get(chunk.chunk_id)
            if anchor_document_chunk is None:
                continue

            for document_chunk in document_chunks:
                distance = abs(
                    document_chunk.sequence_number - anchor_document_chunk.sequence_number
                )
                if distance == 0 or distance > self.neighbor_window:
                    continue

                self._append_chunk(
                    expanded,
                    seen,
                    self._to_retrieved_chunk(
                        document_chunk=document_chunk,
                        anchor_chunk=chunk,
                        distance=distance,
                    ),
                )

        return expanded

    @staticmethod
    def _append_chunk(
        expanded: list[RetrievedChunk],
        seen: set[str],
        chunk: RetrievedChunk,
    ) -> None:
        if chunk.chunk_id in seen:
            return

        seen.add(chunk.chunk_id)
        expanded.append(chunk)

    @staticmethod
    def _to_retrieved_chunk(
        *,
        document_chunk,
        anchor_chunk: RetrievedChunk,
        distance: int,
    ) -> RetrievedChunk:
        metadata = {
            "anchor_chunk_id": anchor_chunk.chunk_id,
            "context_distance": str(distance),
        }

        return RetrievedChunk(
            chunk_id=document_chunk.chunk_id,
            document_id=document_chunk.document_id,
            content=document_chunk.content,
            score=max(anchor_chunk.score - (distance * 0.01), 0.0),
            retrieval_source="context_expansion",
            chunk_type=document_chunk.chunk_type,
            section_id=document_chunk.section_id,
            section_path=list(document_chunk.section_path),
            source=document_chunk.source,
            metadata=metadata,
        )

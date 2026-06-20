from dataclasses import dataclass, field
from typing import Callable

from src.application.contracts.retrieval import VectorStore
from src.application.services.ai import EmbeddingService
from src.domain.document import DocumentChunk
from src.domain.document.value_objects import ChunkStatistics
from src.shared.activity import ActivityContext
from src.shared.exceptions import InfrastructureError
from src.shared.execution import tracked_action


@dataclass(slots=True)
class EmbeddedChunk(DocumentChunk):
    embedding: list[float] = field(default_factory=list)


class EmbeddingWorkflow:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    @tracked_action(
        action="embedding.chunks_stored",
        entity_type="chunk",
        activity=True,
        audit=False,
        event=False,
    )
    def embed_and_store_chunks(
        self,
        chunks: list[DocumentChunk],
        activity_context: ActivityContext | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> list[EmbeddedChunk]:
        if not chunks:
            self._emit_progress(
                progress_callback,
                "No chunks to embed; skipping vector storage.",
            )
            return []

        self._emit_progress(
            progress_callback,
            f"Generating embeddings for {len(chunks)} chunk(s)...",
        )
        embeddings = self.embedding_service.embed_chunks(
            chunks,
            activity_context=activity_context,
        )

        if len(embeddings) != len(chunks):
            raise InfrastructureError(
                "Embedding count does not match chunk count.",
                details={
                    "chunk_count": len(chunks),
                    "embedding_count": len(embeddings),
                },
            )

        embedded_chunks = [
            self._build_embedded_chunk(chunk, embedding)
            for chunk, embedding in zip(chunks, embeddings)
        ]

        self._emit_progress(
            progress_callback,
            f"Saving {len(embedded_chunks)} embedded chunk vector(s)...",
        )
        self.vector_store.save_chunk_vectors(embedded_chunks)
        self._emit_progress(
            progress_callback,
            "Embedding and vector storage completed.",
        )
        return embedded_chunks

    @staticmethod
    def _build_embedded_chunk(
        chunk: DocumentChunk,
        embedding: list[float],
    ) -> EmbeddedChunk:
        return EmbeddedChunk(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            section_id=chunk.section_id,
            content=chunk.content,
            chunk_type=chunk.chunk_type,
            section_path=list(chunk.section_path),
            element_ids=list(chunk.element_ids),
            table_ids=list(chunk.table_ids),
            picture_ids=list(chunk.picture_ids),
            source=chunk.source,
            sequence_number=chunk.sequence_number,
            chunk_index=chunk.chunk_index,
            chunk_total=chunk.chunk_total,
            embedding_text=chunk.embedding_text,
            statistics=EmbeddingWorkflow._clone_statistics(chunk.statistics),
            audit=chunk.audit,
            embedding=list(embedding),
        )

    @staticmethod
    def _clone_statistics(
        statistics: ChunkStatistics | None,
    ) -> ChunkStatistics | None:
        if statistics is None:
            return None

        return ChunkStatistics(
            char_count=statistics.char_count,
            token_count_estimate=statistics.token_count_estimate,
        )

    @staticmethod
    def _emit_progress(
        progress_callback: Callable[[str], None] | None,
        message: str,
    ) -> None:
        if progress_callback is not None:
            progress_callback(message)

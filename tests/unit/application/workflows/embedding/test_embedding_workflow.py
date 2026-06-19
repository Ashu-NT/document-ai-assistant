import pytest

from src.application.workflows.embedding import EmbeddingWorkflow
from src.shared.exceptions import InfrastructureError


class FakeEmbeddingService:
    def __init__(self, vectors: list[list[float]]) -> None:
        self.vectors = vectors
        self.calls = []

    def embed_chunks(self, chunks, activity_context=None) -> list[list[float]]:
        self.calls.append(chunks)
        return self.vectors


class FailingEmbeddingService:
    def embed_chunks(self, chunks, activity_context=None) -> list[list[float]]:
        raise InfrastructureError("Embedding provider failed.")


class FakeVectorStore:
    def __init__(self) -> None:
        self.saved_chunks = []
        self.save_calls = 0

    def save_chunk_vectors(self, chunks) -> None:
        self.save_calls += 1
        self.saved_chunks.append(chunks)

    def search(self, query):
        return []

    def delete_document_vectors(self, document_id: str) -> None:
        return None


def clone_chunk(sample_chunk, *, chunk_id: str, content: str):
    return sample_chunk.__class__(
        chunk_id=chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=content,
        chunk_type=sample_chunk.chunk_type,
        section_path=sample_chunk.section_path,
        element_ids=sample_chunk.element_ids,
        table_ids=sample_chunk.table_ids,
        picture_ids=sample_chunk.picture_ids,
        source=sample_chunk.source,
        sequence_number=sample_chunk.sequence_number,
        chunk_index=sample_chunk.chunk_index,
        chunk_total=sample_chunk.chunk_total,
        embedding_text=sample_chunk.embedding_text,
    )


def test_embed_and_store_chunks_calls_embedding_service_and_vector_store(
    sample_chunk,
) -> None:
    second_chunk = clone_chunk(
        sample_chunk,
        chunk_id="chunk_002",
        content="Inspect the pump housing for visible leaks every 500 hours.",
    )
    embedding_service = FakeEmbeddingService(
        [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]
    )
    vector_store = FakeVectorStore()
    workflow = EmbeddingWorkflow(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = workflow.embed_and_store_chunks([sample_chunk, second_chunk])

    assert embedding_service.calls == [[sample_chunk, second_chunk]]
    assert vector_store.save_calls == 1
    assert len(vector_store.saved_chunks) == 1
    saved_chunks = vector_store.saved_chunks[0]
    assert len(saved_chunks) == 2
    assert saved_chunks[0].chunk_id == sample_chunk.chunk_id
    assert saved_chunks[0].embedding == [0.1, 0.2, 0.3]
    assert saved_chunks[1].chunk_id == second_chunk.chunk_id
    assert saved_chunks[1].embedding == [0.4, 0.5, 0.6]
    assert len(result) == 2
    assert result[0].embedding == [0.1, 0.2, 0.3]
    assert result[1].embedding == [0.4, 0.5, 0.6]


def test_embed_and_store_chunks_handles_empty_list() -> None:
    embedding_service = FakeEmbeddingService([])
    vector_store = FakeVectorStore()
    workflow = EmbeddingWorkflow(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    result = workflow.embed_and_store_chunks([])

    assert result == []
    assert embedding_service.calls == []
    assert vector_store.save_calls == 0


def test_embed_and_store_chunks_does_not_swallow_embedding_errors(
    sample_chunk,
) -> None:
    vector_store = FakeVectorStore()
    workflow = EmbeddingWorkflow(
        embedding_service=FailingEmbeddingService(),
        vector_store=vector_store,
    )

    with pytest.raises(InfrastructureError):
        workflow.embed_and_store_chunks([sample_chunk])

    assert vector_store.save_calls == 0


def test_embed_and_store_chunks_rejects_vector_count_mismatch(
    sample_chunk,
) -> None:
    embedding_service = FakeEmbeddingService([])
    vector_store = FakeVectorStore()
    workflow = EmbeddingWorkflow(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    with pytest.raises(InfrastructureError):
        workflow.embed_and_store_chunks([sample_chunk])

    assert vector_store.save_calls == 0

from qdrant_client.http.models import models

import pytest

from src.domain.common import DocumentType
from src.domain.document import Document, DocumentGraph
from src.domain.document.value_objects import DocumentHashes
from src.application.workflows.embedding.embedding_workflow import EmbeddedChunk
from src.infrastructure.retrieval.vector import QdrantVectorStore
from src.shared.exceptions import VectorStoreError


class FakeQdrantClient:
    def __init__(self) -> None:
        self.upsert_calls = []
        self.query_points_calls = []
        self.delete_calls = []

    def upsert(self, **kwargs) -> None:
        self.upsert_calls.append(kwargs)

    def query_points(self, **kwargs):
        self.query_points_calls.append(kwargs)
        return models.QueryResponse(
            points=[
                models.ScoredPoint(
                    id="point_001",
                    version=1,
                    score=0.93,
                    payload={
                        "chunk_id": "chunk_001",
                        "document_id": "doc_001",
                        "section_id": "sec_001",
                        "section_path": ["Maintenance Schedule"],
                        "chunk_type": "maintenance_interval",
                        "content": "Replace hydraulic filter every 1000 operating hours.",
                        "sequence_number": 1,
                        "chunk_index": 1,
                        "chunk_total": 1,
                        "page_start": 10,
                        "page_end": 10,
                    },
                )
            ]
        )

    def delete(self, **kwargs) -> None:
        self.delete_calls.append(kwargs)


class FakeVectorMappingRepository:
    def __init__(self) -> None:
        self.save_calls = []

    def save_mapping(self, **kwargs) -> None:
        self.save_calls.append(kwargs)

    def list_chunk_ids_by_document(self, document_id: str) -> list[str]:
        return ["chunk_001"]

    def list_qdrant_point_ids_by_document(self, document_id: str) -> list[str]:
        return ["point_001"]

    def delete_document_mappings(self, document_id: str) -> None:
        return None


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.calls = []

    def embed_text(self, text: str) -> list[float]:
        self.calls.append(text)
        return [0.1, 0.2, 0.3]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise AssertionError("embed_batch should not be called in this test")


class FakeDocumentRepository:
    def get_document_graph(self, document_id: str):
        return DocumentGraph(
            document=Document(
                document_id=document_id,
                file_name="sample.pdf",
                file_path="sample.pdf",
                hashes=DocumentHashes(file_hash="hash", content_hash="content_hash"),
                document_type=DocumentType.MANUAL,
            )
        )


def test_qdrant_vector_store_search_embeds_query_and_maps_results(
    sample_retrieval_query,
) -> None:
    client = FakeQdrantClient()
    provider = FakeEmbeddingProvider()
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
    )

    results = store.search(sample_retrieval_query)

    assert provider.calls == [sample_retrieval_query.query_text]
    assert client.query_points_calls[0]["collection_name"] == "document_chunks"
    assert client.query_points_calls[0]["limit"] == sample_retrieval_query.top_k
    assert results[0].chunk_id == "chunk_001"
    assert results[0].section_path == ["Maintenance Schedule"]
    assert results[0].retrieval_source == "dense"


def test_qdrant_vector_store_search_requires_query_embedding_provider(
    sample_retrieval_query,
) -> None:
    store = QdrantVectorStore(
        client=FakeQdrantClient(),
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=None,
    )

    with pytest.raises(VectorStoreError):
        store.search(sample_retrieval_query)


def test_qdrant_vector_store_saves_chunk_payload_and_mapping(sample_chunk) -> None:
    client = FakeQdrantClient()
    mapping_repository = FakeVectorMappingRepository()
    store = QdrantVectorStore(
        client=client,
        mapping_repository=mapping_repository,
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=FakeEmbeddingProvider(),
        document_repository=FakeDocumentRepository(),
    )
    embedded_chunk = EmbeddedChunk(
        chunk_id=sample_chunk.chunk_id,
        document_id=sample_chunk.document_id,
        section_id=sample_chunk.section_id,
        content=sample_chunk.content,
        chunk_type=sample_chunk.chunk_type,
        section_path=list(sample_chunk.section_path),
        element_ids=list(sample_chunk.element_ids),
        source=sample_chunk.source,
        embedding_text=sample_chunk.embedding_text,
        embedding=[0.1, 0.2, 0.3],
    )

    store.save_chunk_vectors([embedded_chunk])

    assert len(client.upsert_calls) == 1
    assert client.upsert_calls[0]["points"][0].payload["content"] == sample_chunk.content
    assert client.upsert_calls[0]["points"][0].payload["document_type"] == "manual"
    assert len(mapping_repository.save_calls) == 1
    assert mapping_repository.save_calls[0]["chunk_id"] == sample_chunk.chunk_id


def test_qdrant_vector_store_search_builds_document_type_filter(
    sample_retrieval_query,
) -> None:
    client = FakeQdrantClient()
    provider = FakeEmbeddingProvider()
    sample_retrieval_query.document_types = [DocumentType.MANUAL]
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
    )

    store.search(sample_retrieval_query)

    query_filter = client.query_points_calls[0]["query_filter"]
    assert query_filter is not None
    assert len(query_filter.must) == 2
    assert {condition.key for condition in query_filter.must} == {
        "chunk_type",
        "document_type",
    }


def test_qdrant_vector_store_search_filters_by_document_id_when_set(
    sample_retrieval_query,
) -> None:
    client = FakeQdrantClient()
    provider = FakeEmbeddingProvider()
    sample_retrieval_query.document_id = "doc_fwc12"
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
    )

    store.search(sample_retrieval_query)

    query_filter = client.query_points_calls[0]["query_filter"]
    assert query_filter is not None
    filter_keys = {c.key for c in query_filter.must}
    assert "document_id" in filter_keys
    doc_condition = next(c for c in query_filter.must if c.key == "document_id")
    assert doc_condition.match.value == "doc_fwc12"


def test_qdrant_vector_store_search_no_filter_when_document_id_not_set(
    sample_retrieval_query,
) -> None:
    from src.domain.retrieval import RetrievalQuery

    client = FakeQdrantClient()
    provider = FakeEmbeddingProvider()
    bare_query = RetrievalQuery(
        query_id="q_bare",
        query_text="What is the maintenance interval?",
    )
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
    )

    store.search(bare_query)

    query_filter = client.query_points_calls[0]["query_filter"]
    assert query_filter is None

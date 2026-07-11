import pytest

pytest.importorskip("qdrant_client")

from qdrant_client.http.models import models

from src.domain.common import DocumentType

from src.domain.document import Document, DocumentGraph

from src.domain.document.value_objects import ChunkStatistics

from src.domain.document.value_objects import DocumentHashes

from src.application.workflows.embedding.embedding_workflow import EmbeddedChunk

from src.infrastructure.retrieval.vector import QdrantVectorStore

from src.shared.exceptions import VectorStoreError

class FakeQdrantClient:
    def __init__(self) -> None:
        self.upsert_calls = []
        self.query_points_calls = []
        self.delete_calls = []
        self.identifier_values_payload: list[str] | None = None

    def upsert(self, **kwargs) -> None:
        self.upsert_calls.append(kwargs)

    def query_points(self, **kwargs):
        self.query_points_calls.append(kwargs)
        payload = {
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
            "char_count": 53,
            "token_count_estimate": 7,
        }
        if self.identifier_values_payload is not None:
            payload["identifier_values"] = self.identifier_values_payload
        return models.QueryResponse(
            points=[
                models.ScoredPoint(
                    id="point_001",
                    version=1,
                    score=0.93,
                    payload=payload,
                )
            ]
        )

    def delete(self, **kwargs) -> None:
        self.delete_calls.append(kwargs)

class FakeVectorMappingRepository:
    def __init__(self) -> None:
        self.save_calls = []

    def save_mappings(self, mappings: list[dict]) -> None:
        self.save_calls.extend(mappings)

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
    def __init__(self) -> None:
        self.get_document_graph_calls: list[str] = []

    def get_document_graph(self, document_id: str):
        self.get_document_graph_calls.append(document_id)
        return DocumentGraph(
            document=Document(
                document_id=document_id,
                file_name="sample.pdf",
                file_path="sample.pdf",
                hashes=DocumentHashes(file_hash="hash", content_hash="content_hash"),
                document_type=DocumentType.MANUAL,
            )
        )

def test_qdrant_vector_store_search_maps_identifier_values_from_payload(
    sample_retrieval_query,
) -> None:
    client = FakeQdrantClient()
    client.identifier_values_payload = ["HP-001", "SN-9999"]
    provider = FakeEmbeddingProvider()
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
    )

    results = store.search(sample_retrieval_query)

    assert results[0].identifier_values == ["HP-001", "SN-9999"]

def test_qdrant_vector_store_search_defaults_identifier_values_to_empty_list(
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

    assert results[0].identifier_values == []

def test_qdrant_vector_store_search_omits_identifier_filter_by_default(
    sample_retrieval_query,
) -> None:
    client = FakeQdrantClient()
    provider = FakeEmbeddingProvider()
    sample_retrieval_query.detected_identifiers = ["HP-001"]
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
    )

    store.search(sample_retrieval_query)

    query_filter = client.query_points_calls[0]["query_filter"]
    filter_keys = {c.key for c in query_filter.must}
    assert "identifier_values" not in filter_keys

def test_qdrant_vector_store_search_applies_identifier_filter_when_enabled(
    sample_retrieval_query,
) -> None:
    client = FakeQdrantClient()
    provider = FakeEmbeddingProvider()
    sample_retrieval_query.detected_identifiers = ["HP-001", "SN-9999"]
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
        enable_identifier_filter=True,
    )

    store.search(sample_retrieval_query)

    query_filter = client.query_points_calls[0]["query_filter"]
    identifier_condition = next(
        c for c in query_filter.must if c.key == "identifier_values"
    )
    assert set(identifier_condition.match.any) == {"HP-001", "SN-9999"}

def test_qdrant_vector_store_identifier_filter_normalizes_case_to_match_stored_payload(
    sample_retrieval_query,
) -> None:
    """`identifier_values` payloads are stored uppercased via `normalize_identifier`
    (see `_identifier_values_by_chunk_id`), but `RetrievalQueryIdentifierExtractor`
    lowercases its extracted tokens for other consumers (e.g. case-insensitive SQL
    ILIKE matching). Without normalizing here too, Qdrant's exact-match `MatchAny`
    would never match a real-world lowercase-extracted identifier against the
    uppercase stored value — silently returning zero results for every identifier
    query the moment this filter is enabled."""
    client = FakeQdrantClient()
    provider = FakeEmbeddingProvider()
    # Mirrors what RetrievalQueryIdentifierExtractor actually produces: lowercase,
    # not the idealized pre-uppercased fixture values used in the test above.
    sample_retrieval_query.detected_identifiers = ["hp-001", "sn-9999"]
    store = QdrantVectorStore(
        client=client,
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=provider,
        enable_identifier_filter=True,
    )

    store.search(sample_retrieval_query)

    query_filter = client.query_points_calls[0]["query_filter"]
    identifier_condition = next(
        c for c in query_filter.must if c.key == "identifier_values"
    )
    assert set(identifier_condition.match.any) == {"HP-001", "SN-9999"}

def test_qdrant_vector_store_search_enabled_but_no_identifiers_detected_adds_no_filter(
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
        enable_identifier_filter=True,
    )

    store.search(sample_retrieval_query)

    query_filter = client.query_points_calls[0]["query_filter"]
    filter_keys = {c.key for c in query_filter.must}
    assert "identifier_values" not in filter_keys

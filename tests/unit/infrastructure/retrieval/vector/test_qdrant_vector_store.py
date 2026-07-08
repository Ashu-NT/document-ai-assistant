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
    assert results[0].statistics is not None
    assert results[0].statistics.char_count == 53
    assert results[0].statistics.token_count_estimate == 7


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
        statistics=ChunkStatistics(char_count=123, token_count_estimate=17),
        embedding=[0.1, 0.2, 0.3],
    )

    store.save_chunk_vectors([embedded_chunk])

    assert len(client.upsert_calls) == 1
    assert client.upsert_calls[0]["points"][0].payload["content"] == sample_chunk.content
    assert client.upsert_calls[0]["points"][0].payload["document_type"] == "manual"
    assert client.upsert_calls[0]["points"][0].payload["char_count"] == 123
    assert client.upsert_calls[0]["points"][0].payload["token_count_estimate"] == 17
    assert len(mapping_repository.save_calls) == 1
    assert mapping_repository.save_calls[0]["chunk_id"] == sample_chunk.chunk_id


def test_qdrant_vector_store_saves_load_each_document_graph_only_once(
    sample_chunk,
) -> None:
    """document_type and identifier_values both need per-document graph
    data, but the graph should only be fetched once per unique document,
    not once per lookup."""
    document_repository = FakeDocumentRepository()
    store = QdrantVectorStore(
        client=FakeQdrantClient(),
        mapping_repository=FakeVectorMappingRepository(),
        collection_name="document_chunks",
        embedding_model="BAAI/bge-small-en-v1.5",
        query_embedding_provider=FakeEmbeddingProvider(),
        document_repository=document_repository,
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

    assert document_repository.get_document_graph_calls == [sample_chunk.document_id]


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


# --- identifier_values read-back -----------------------------------------------

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


# --- identifier_values dense filter (opt-in) ------------------------------------

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

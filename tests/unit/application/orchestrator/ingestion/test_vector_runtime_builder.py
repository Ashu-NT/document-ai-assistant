from __future__ import annotations

from types import SimpleNamespace

import pytest
from qdrant_client.models import Distance, PayloadSchemaType

from src.application.orchestrator.ingestion import vector_runtime_builder
from src.application.orchestrator.ingestion.vector_runtime_builder import (
    build_embedding_workflow,
    build_vector_store,
    create_qdrant_client,
    ensure_qdrant_collection,
    resolve_qdrant_distance,
)


# --- resolve_qdrant_distance ---------------------------------------------------

@pytest.mark.parametrize(
    "value,expected",
    [
        ("cosine", Distance.COSINE),
        ("COSINE", Distance.COSINE),
        ("dot", Distance.DOT),
        ("euclid", Distance.EUCLID),
        ("manhattan", Distance.MANHATTAN),
        ("  dot  ", Distance.DOT),
    ],
)
def test_resolve_qdrant_distance_known_values(value, expected):
    assert resolve_qdrant_distance(value) == expected


def test_resolve_qdrant_distance_unknown_value_defaults_to_cosine():
    assert resolve_qdrant_distance("not-a-real-distance") == Distance.COSINE


# --- create_qdrant_client -------------------------------------------------------

class _FakeQdrantClient:
    def __init__(self, *, path=None, host=None, port=None):
        self.path = path
        self.host = host
        self.port = port


def test_create_qdrant_client_uses_local_path_for_local_mode(monkeypatch):
    monkeypatch.setattr(vector_runtime_builder, "QdrantClient", _FakeQdrantClient)
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings,
        "mode",
        "local",
        raising=False,
    )
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings,
        "path",
        "qdrant_data",
        raising=False,
    )

    client = create_qdrant_client()

    assert isinstance(client, _FakeQdrantClient)
    assert client.path == str(vector_runtime_builder.qdrant_settings.storage_path)
    assert client.host is None


def test_create_qdrant_client_uses_host_port_for_remote_mode(monkeypatch):
    monkeypatch.setattr(vector_runtime_builder, "QdrantClient", _FakeQdrantClient)
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "mode", "remote", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "host", "qdrant.internal", raising=False
    )
    monkeypatch.setattr(vector_runtime_builder.qdrant_settings, "port", 6333, raising=False)

    client = create_qdrant_client()

    assert isinstance(client, _FakeQdrantClient)
    assert client.path is None
    assert client.host == "qdrant.internal"
    assert client.port == 6333


# --- ensure_qdrant_collection ---------------------------------------------------

class _FakeCollectionClient:
    def __init__(self, *, exists: bool):
        self._exists = exists
        self.created_with = None
        self.payload_index_calls = []

    def collection_exists(self, name):
        return self._exists

    def create_collection(self, *, collection_name, vectors_config):
        self.created_with = (collection_name, vectors_config)

    def create_payload_index(self, *, collection_name, field_name, field_schema):
        self.payload_index_calls.append((collection_name, field_name, field_schema))


def test_ensure_qdrant_collection_skips_creation_when_already_exists(monkeypatch):
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "collection", "document_chunks", raising=False
    )
    client = _FakeCollectionClient(exists=True)

    ensure_qdrant_collection(client)

    assert client.created_with is None


def test_ensure_qdrant_collection_creates_when_missing(monkeypatch):
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "collection", "document_chunks", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "vector_distance", "cosine", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.embedding_settings, "dimensions", 384, raising=False
    )
    client = _FakeCollectionClient(exists=False)

    ensure_qdrant_collection(client)

    assert client.created_with is not None
    collection_name, vectors_config = client.created_with
    assert collection_name == "document_chunks"
    assert vectors_config.size == 384
    assert vectors_config.distance == Distance.COSINE


def test_ensure_qdrant_collection_creates_identifier_values_payload_index_for_new_collection(
    monkeypatch,
):
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "collection", "document_chunks", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "vector_distance", "cosine", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.embedding_settings, "dimensions", 384, raising=False
    )
    client = _FakeCollectionClient(exists=False)

    ensure_qdrant_collection(client)

    assert client.payload_index_calls == [
        ("document_chunks", "identifier_values", PayloadSchemaType.KEYWORD)
    ]


def test_ensure_qdrant_collection_creates_identifier_values_payload_index_for_existing_collection(
    monkeypatch,
):
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "collection", "document_chunks", raising=False
    )
    client = _FakeCollectionClient(exists=True)

    ensure_qdrant_collection(client)

    assert client.payload_index_calls == [
        ("document_chunks", "identifier_values", PayloadSchemaType.KEYWORD)
    ]


# --- build_vector_store / build_embedding_workflow ------------------------------

class _FakeVectorStore:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeEmbeddingService:
    def __init__(self, provider):
        self.provider = provider


class _FakeEmbeddingWorkflow:
    def __init__(self, *, embedding_service, vector_store):
        self.embedding_service = embedding_service
        self.vector_store = vector_store


def test_build_vector_store_wires_client_and_ensures_collection(monkeypatch):
    fake_client = _FakeCollectionClient(exists=True)
    monkeypatch.setattr(vector_runtime_builder, "create_qdrant_client", lambda: fake_client)
    monkeypatch.setattr(vector_runtime_builder, "QdrantVectorStore", _FakeVectorStore)
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "collection", "document_chunks", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.embedding_settings, "model_name", "bge-small", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.retrieval_settings,
        "enable_dense_identifier_filter",
        False,
        raising=False,
    )
    uow = SimpleNamespace(vector_mappings="mappings", documents="documents")
    embedding_provider = object()

    vector_store, client = build_vector_store(
        unit_of_work=uow,
        embedding_provider=embedding_provider,
    )

    assert client is fake_client
    assert isinstance(vector_store, _FakeVectorStore)
    assert vector_store.kwargs["client"] is fake_client
    assert vector_store.kwargs["mapping_repository"] == "mappings"
    assert vector_store.kwargs["document_repository"] == "documents"
    assert vector_store.kwargs["collection_name"] == "document_chunks"
    assert vector_store.kwargs["embedding_model"] == "bge-small"
    assert vector_store.kwargs["query_embedding_provider"] is embedding_provider
    assert vector_store.kwargs["enable_identifier_filter"] is False


def test_build_vector_store_passes_through_enabled_identifier_filter_flag(monkeypatch):
    fake_client = _FakeCollectionClient(exists=True)
    monkeypatch.setattr(vector_runtime_builder, "create_qdrant_client", lambda: fake_client)
    monkeypatch.setattr(vector_runtime_builder, "QdrantVectorStore", _FakeVectorStore)
    monkeypatch.setattr(
        vector_runtime_builder.qdrant_settings, "collection", "document_chunks", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.embedding_settings, "model_name", "bge-small", raising=False
    )
    monkeypatch.setattr(
        vector_runtime_builder.retrieval_settings,
        "enable_dense_identifier_filter",
        True,
        raising=False,
    )
    uow = SimpleNamespace(vector_mappings="mappings", documents="documents")

    vector_store, _ = build_vector_store(
        unit_of_work=uow,
        embedding_provider=object(),
    )

    assert vector_store.kwargs["enable_identifier_filter"] is True


def test_build_embedding_workflow_wires_service_and_store(monkeypatch):
    monkeypatch.setattr(vector_runtime_builder, "EmbeddingService", _FakeEmbeddingService)
    monkeypatch.setattr(vector_runtime_builder, "EmbeddingWorkflow", _FakeEmbeddingWorkflow)
    vector_store = _FakeVectorStore()
    embedding_provider = object()

    workflow = build_embedding_workflow(
        vector_store=vector_store,
        embedding_provider=embedding_provider,
    )

    assert isinstance(workflow, _FakeEmbeddingWorkflow)
    assert isinstance(workflow.embedding_service, _FakeEmbeddingService)
    assert workflow.embedding_service.provider is embedding_provider
    assert workflow.vector_store is vector_store

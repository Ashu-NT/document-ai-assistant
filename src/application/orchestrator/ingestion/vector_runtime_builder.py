from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.application.contracts import UnitOfWork
from src.application.contracts.ai import EmbeddingProvider
from src.application.services.ai import EmbeddingService
from src.application.workflows.embedding import EmbeddingWorkflow
from src.config.settings import embedding_settings, qdrant_settings, retrieval_settings

_IDENTIFIER_VALUES_FIELD = "identifier_values"

if TYPE_CHECKING:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance
    from src.infrastructure.retrieval.vector import QdrantVectorStore

QdrantClient = None
QdrantVectorStore = None


def _resolve_qdrant_client_class():
    if QdrantClient is not None:
        return QdrantClient
    from qdrant_client import QdrantClient as imported_qdrant_client

    return imported_qdrant_client


def _resolve_qdrant_model_types():
    from qdrant_client.models import (
        Distance as imported_distance,
        PayloadSchemaType as imported_payload_schema_type,
        VectorParams as imported_vector_params,
    )

    return (
        imported_distance,
        imported_payload_schema_type,
        imported_vector_params,
    )


def _resolve_qdrant_vector_store_class():
    if QdrantVectorStore is not None:
        return QdrantVectorStore
    from src.infrastructure.retrieval.vector import (
        QdrantVectorStore as imported_qdrant_vector_store,
    )

    return imported_qdrant_vector_store


def resolve_qdrant_distance(value: str) -> Distance:
    distance_type, _, _ = _resolve_qdrant_model_types()
    distance_by_name: dict[str, Any] = {
        "cosine": distance_type.COSINE,
        "dot": distance_type.DOT,
        "euclid": distance_type.EUCLID,
        "manhattan": distance_type.MANHATTAN,
    }
    return distance_by_name.get(value.strip().lower(), distance_type.COSINE)


def create_qdrant_client() -> QdrantClient:
    qdrant_client_class = _resolve_qdrant_client_class()
    if qdrant_settings.mode.lower() == "local":
        return qdrant_client_class(path=str(qdrant_settings.storage_path))

    return qdrant_client_class(
        host=qdrant_settings.host,
        port=qdrant_settings.port,
    )


def ensure_qdrant_collection(client: QdrantClient) -> None:
    _, payload_schema_type, vector_params = _resolve_qdrant_model_types()
    if not client.collection_exists(qdrant_settings.collection):
        client.create_collection(
            collection_name=qdrant_settings.collection,
            vectors_config=vector_params(
                size=embedding_settings.dimensions,
                distance=resolve_qdrant_distance(qdrant_settings.vector_distance),
            ),
        )

    # Idempotent: safe to call on every startup, including against a
    # collection that already has the index. A no-op against local-mode
    # Qdrant (payload indexes only take effect on server-mode Qdrant), but
    # cheap to create either way so the collection is ready for server-mode
    # deployment without a separate migration step.
    client.create_payload_index(
        collection_name=qdrant_settings.collection,
        field_name=_IDENTIFIER_VALUES_FIELD,
        field_schema=payload_schema_type.KEYWORD,
    )


def build_vector_store(
    *,
    unit_of_work: UnitOfWork,
    embedding_provider: EmbeddingProvider,
) -> tuple[QdrantVectorStore, QdrantClient]:
    """Create the Qdrant-backed vector store, ensuring its collection exists."""
    client = create_qdrant_client()
    vector_store_class = _resolve_qdrant_vector_store_class()
    vector_store = vector_store_class(
        client=client,
        mapping_repository=unit_of_work.vector_mappings,
        collection_name=qdrant_settings.collection,
        embedding_model=embedding_settings.model_name,
        query_embedding_provider=embedding_provider,
        document_repository=unit_of_work.documents,
        enable_identifier_filter=retrieval_settings.enable_dense_identifier_filter,
    )
    ensure_qdrant_collection(client)
    return vector_store, client


def build_embedding_workflow(
    *,
    vector_store: QdrantVectorStore,
    embedding_provider: EmbeddingProvider,
) -> EmbeddingWorkflow:
    return EmbeddingWorkflow(
        embedding_service=EmbeddingService(embedding_provider),
        vector_store=vector_store,
    )

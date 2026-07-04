from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

from src.application.contracts import UnitOfWork
from src.application.contracts.ai import EmbeddingProvider
from src.application.services.ai import EmbeddingService
from src.application.workflows.embedding import EmbeddingWorkflow
from src.config.settings import embedding_settings, qdrant_settings, retrieval_settings
from src.infrastructure.retrieval.vector import QdrantVectorStore

_IDENTIFIER_VALUES_FIELD = "identifier_values"

_DISTANCE_BY_NAME: dict[str, Distance] = {
    "cosine": Distance.COSINE,
    "dot": Distance.DOT,
    "euclid": Distance.EUCLID,
    "manhattan": Distance.MANHATTAN,
}


def resolve_qdrant_distance(value: str) -> Distance:
    return _DISTANCE_BY_NAME.get(value.strip().lower(), Distance.COSINE)


def create_qdrant_client() -> QdrantClient:
    if qdrant_settings.mode.lower() == "local":
        return QdrantClient(path=str(qdrant_settings.storage_path))

    return QdrantClient(
        host=qdrant_settings.host,
        port=qdrant_settings.port,
    )


def ensure_qdrant_collection(client: QdrantClient) -> None:
    if not client.collection_exists(qdrant_settings.collection):
        client.create_collection(
            collection_name=qdrant_settings.collection,
            vectors_config=VectorParams(
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
        field_schema=PayloadSchemaType.KEYWORD,
    )


def build_vector_store(
    *,
    unit_of_work: UnitOfWork,
    embedding_provider: EmbeddingProvider,
) -> tuple[QdrantVectorStore, QdrantClient]:
    """Create the Qdrant-backed vector store, ensuring its collection exists."""
    client = create_qdrant_client()
    vector_store = QdrantVectorStore(
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

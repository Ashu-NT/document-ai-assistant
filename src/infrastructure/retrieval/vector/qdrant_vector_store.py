from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from src.application.contracts.retrieval import VectorStore
from src.domain.document.entities import DocumentChunk
from src.domain.retrieval import RetrievalQuery, RetrievedChunk
from src.infrastructure.db.repositories.retrieval import (
    SqlAlchemyVectorMappingRepository,
)
from src.infrastructure.retrieval.vector.qdrant_payload_mapper import (
    QdrantPayloadMapper,
)
from src.shared.exceptions import VectorStoreError


class QdrantVectorStore(VectorStore):
    def __init__(
        self,
        *,
        client: QdrantClient,
        mapping_repository: SqlAlchemyVectorMappingRepository,
        collection_name: str,
        embedding_model: str,
    ) -> None:
        self.client = client
        self.mapping_repository = mapping_repository
        self.collection_name = collection_name
        self.embedding_model = embedding_model

    def save_chunk_vectors(self, chunks: list[DocumentChunk]) -> None:
        points: list[PointStruct] = []

        for chunk in chunks:
            embedding = getattr(chunk, "embedding", None)

            if embedding is None:
                raise VectorStoreError(
                    "Cannot save chunk vector because chunk has no embedding.",
                    details={"chunk_id": chunk.chunk_id},
                )

            point_id = str(uuid4())

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=QdrantPayloadMapper.from_chunk(chunk),
                )
            )

            self.mapping_repository.save_mapping(
                vector_id=f"vector_{uuid4().hex}",
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                qdrant_collection=self.collection_name,
                qdrant_point_id=point_id,
                embedding_model=self.embedding_model,
            )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
        except Exception as exc:
            raise VectorStoreError(
                "Failed to save chunk vectors to Qdrant.",
                details={"collection_name": self.collection_name},
            ) from exc

    def search(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        raise NotImplementedError(
            "Qdrant search requires query embeddings. Add EmbeddingService first."
        )

    def delete_document_vectors(self, document_id: str) -> None:
        chunk_ids = self.mapping_repository.list_chunk_ids_by_document(document_id)

        if not chunk_ids:
            return

        point_ids = (
            self.mapping_repository
            .list_qdrant_point_ids_by_document(document_id)
        )

        if not point_ids:
            return

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=point_ids,
        )
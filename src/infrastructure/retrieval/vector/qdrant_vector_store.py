import hashlib
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchAny, PointStruct

from src.application.contracts.ai import EmbeddingProvider
from src.application.contracts.document import DocumentRepository
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
        query_embedding_provider: EmbeddingProvider | None = None,
        document_repository: DocumentRepository | None = None,
    ) -> None:
        self.client = client
        self.mapping_repository = mapping_repository
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.query_embedding_provider = query_embedding_provider
        self.document_repository = document_repository

    def save_chunk_vectors(self, chunks: list[DocumentChunk]) -> None:
        points: list[PointStruct] = []
        document_types_by_id = self._document_types_by_id(chunks)

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
                    payload=QdrantPayloadMapper.from_chunk(
                        chunk,
                        document_type=document_types_by_id.get(chunk.document_id),
                    ),
                )
            )
            self.mapping_repository.save_mapping(
                vector_id=f"vector_{uuid4().hex}",
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                qdrant_collection=self.collection_name,
                qdrant_point_id=point_id,
                embedding_model=self.embedding_model,
                embedding_text_hash=self._embedding_text_hash(chunk),
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
        if self.query_embedding_provider is None:
            raise VectorStoreError(
                "Dense retrieval requires a query embedding provider.",
                details={"collection_name": self.collection_name},
            )

        try:
            query_vector = self.query_embedding_provider.embed_text(
                query.effective_query()
            )
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=self._build_filter(query),
                limit=query.top_k,
                with_payload=True,
                with_vectors=False,
            )
        except Exception as exc:
            raise VectorStoreError(
                "Failed to search chunk vectors in Qdrant.",
                details={
                    "collection_name": self.collection_name,
                    "query_id": query.query_id,
                },
            ) from exc

        return [
            QdrantPayloadMapper.to_retrieved_chunk(
                point,
                retrieval_source="dense",
            )
            for point in response.points
        ]

    def delete_document_vectors(self, document_id: str) -> None:
        chunk_ids = self.mapping_repository.list_chunk_ids_by_document(document_id)
        if not chunk_ids:
            return

        point_ids = self.mapping_repository.list_qdrant_point_ids_by_document(document_id)
        if not point_ids:
            return

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=point_ids,
        )
        self.mapping_repository.delete_document_mappings(document_id)

    def _build_filter(
        self,
        query: RetrievalQuery,
    ) -> Filter | None:
        conditions: list[FieldCondition] = []

        if query.chunk_types:
            conditions.append(
                FieldCondition(
                    key="chunk_type",
                    match=MatchAny(
                        any=[chunk_type.value for chunk_type in query.chunk_types]
                    ),
                )
            )

        if query.document_types:
            conditions.append(
                FieldCondition(
                    key="document_type",
                    match=MatchAny(
                        any=[document_type.value for document_type in query.document_types]
                    ),
                )
            )

        if not conditions:
            return None

        return Filter(must=conditions)

    def _document_types_by_id(
        self,
        chunks: list[DocumentChunk],
    ) -> dict[str, str]:
        if self.document_repository is None:
            return {}

        document_types_by_id: dict[str, str] = {}
        for document_id in {chunk.document_id for chunk in chunks}:
            document_graph = self.document_repository.get_document_graph(document_id)
            if document_graph is None:
                continue
            document_types_by_id[document_id] = document_graph.document.document_type.value
        return document_types_by_id

    @staticmethod
    def _embedding_text_hash(chunk: DocumentChunk) -> str:
        text = chunk.embedding_text or chunk.content
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

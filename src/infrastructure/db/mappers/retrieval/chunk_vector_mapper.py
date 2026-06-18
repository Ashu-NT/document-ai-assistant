from datetime import datetime, timezone

from src.infrastructure.db.orm_models import ChunkVectorORM


class ChunkVectorMapper:
    @staticmethod
    def to_orm(
        *,
        vector_id: str,
        document_id: str,
        chunk_id: str,
        qdrant_collection: str,
        qdrant_point_id: str,
        embedding_model: str,
        embedding_text_hash: str | None = None,
    ) -> ChunkVectorORM:
        return ChunkVectorORM(
            id=vector_id,
            document_id=document_id,
            chunk_id=chunk_id,
            qdrant_collection=qdrant_collection,
            qdrant_point_id=qdrant_point_id,
            embedding_model=embedding_model,
            embedding_text_hash=embedding_text_hash,
            created_at=datetime.now(timezone.utc),
        )
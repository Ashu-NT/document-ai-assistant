from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.infrastructure.db.orm_models import ChunkVectorORM
from src.shared.exceptions import DatabaseError


class SqlAlchemyVectorMappingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_mapping(
        self,
        *,
        vector_id: str,
        document_id: str,
        chunk_id: str,
        qdrant_collection: str,
        qdrant_point_id: str,
        embedding_model: str,
        embedding_text_hash: str | None = None,
    ) -> None:
        try:
            mapping = ChunkVectorORM(
                id=vector_id,
                document_id=document_id,
                chunk_id=chunk_id,
                qdrant_collection=qdrant_collection,
                qdrant_point_id=qdrant_point_id,
                embedding_model=embedding_model,
                embedding_text_hash=embedding_text_hash,
            )

            self.session.merge(mapping)

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save vector mapping.",
                details={
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "qdrant_point_id": qdrant_point_id,
                },
            ) from exc

    def get_qdrant_point_id(self, chunk_id: str) -> str | None:
        try:
            statement = select(ChunkVectorORM.qdrant_point_id).where(
                ChunkVectorORM.chunk_id == chunk_id
            )

            return self.session.execute(statement).scalar_one_or_none()

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to get Qdrant point id for chunk.",
                details={"chunk_id": chunk_id},
            ) from exc

    def list_chunk_ids_by_document(self, document_id: str) -> list[str]:
        try:
            statement = select(ChunkVectorORM.chunk_id).where(
                ChunkVectorORM.document_id == document_id
            )

            return list(self.session.execute(statement).scalars().all())

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to list vector chunk ids by document.",
                details={"document_id": document_id},
            ) from exc
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ChunkVectorORM(Base):
    __tablename__ = "chunk_vectors"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        index=True,
        nullable=False,
    )

    chunk_id: Mapped[str] = mapped_column(
        ForeignKey("chunks.id"),
        index=True,
        nullable=False,
    )

    qdrant_collection: Mapped[str] = mapped_column(String, nullable=False)
    qdrant_point_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )

    embedding_model: Mapped[str] = mapped_column(String, nullable=False)
    embedding_text_hash: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(nullable=False)
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class DocumentClassificationORM(Base):
    __tablename__ = "document_classifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[str] = mapped_column(String, nullable=False)

    predicted_label: Mapped[str] = mapped_column(String, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    model_type: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ChunkClassificationORM(Base):
    __tablename__ = "chunk_classifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    chunk_id: Mapped[str] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=False,
        index=True,
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    chunk_type: Mapped[str] = mapped_column(String, nullable=False)

    predicted_label: Mapped[str] = mapped_column(String, nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    model_type: Mapped[str | None] = mapped_column(String, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
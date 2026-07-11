from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class SemanticRelationshipORM(Base):
    __tablename__ = "semantic_relationships"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    relationship_type: Mapped[str] = mapped_column(String, nullable=False, index=True)

    source_entity_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_entity_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_entity_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    target_entity_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    confidence_score: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)
    evidence: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

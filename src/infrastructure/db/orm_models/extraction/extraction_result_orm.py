from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ExtractionResultORM(Base):
    __tablename__ = "extraction_results"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)
    source_chunk_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempted_chunk_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    unresolved_chunk_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

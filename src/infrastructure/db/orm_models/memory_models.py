from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ConversationMemoryORM(Base):
    __tablename__ = "conversation_memories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ConversationMessageORM(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    conversation_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class MemoryEntryORM(Base):
    __tablename__ = "memory_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    memory_type: Mapped[str] = mapped_column(String, nullable=False)

    source_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    source_type: Mapped[str | None] = mapped_column(String, nullable=True)

    importance_score: Mapped[float | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SemanticMemoryReferenceORM(Base):
    __tablename__ = "semantic_memory_references"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    source_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False)

    vector_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    collection_name: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
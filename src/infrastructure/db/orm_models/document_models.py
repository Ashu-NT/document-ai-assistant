from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base


class DocumentORM(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)

    file_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    content_hash: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(String, nullable=True)
    document_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="unknown",
    )
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    sections: Mapped[list["SectionORM"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class SectionORM(Base):
    __tablename__ = "sections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    parent_section_id: Mapped[str | None] = mapped_column(String, nullable=True)
    section_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sequence_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reading_order_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reading_order_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    overview_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunk_type_signals: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    document: Mapped[DocumentORM] = relationship(back_populates="sections")


class ElementORM(Base):
    __tablename__ = "elements"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        index=True,
        nullable=False,
    )

    element_type: Mapped[str] = mapped_column(String, nullable=False)

    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent_section_id: Mapped[str | None] = mapped_column(
        ForeignKey("sections.id"),
        nullable=True,
        index=True,
    )

    reading_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    bbox_x1: Mapped[float | None] = mapped_column(nullable=True)
    bbox_y1: Mapped[float | None] = mapped_column(nullable=True)
    bbox_x2: Mapped[float | None] = mapped_column(nullable=True)
    bbox_y2: Mapped[float | None] = mapped_column(nullable=True)

    table_id: Mapped[str | None] = mapped_column(String, nullable=True)
    picture_id: Mapped[str | None] = mapped_column(String, nullable=True)

    raw_source_type: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_ref: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ChunkORM(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        index=True,
        nullable=False,
    )

    section_id: Mapped[str | None] = mapped_column(
        ForeignKey("sections.id"),
        nullable=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    chunk_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="general",
    )

    chunk_type_source: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default="deterministic",
    )

    section_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    chunk_total: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    char_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class GeneratedQuestionORM(Base):
    __tablename__ = "generated_questions"

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

    question: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IdentifierORM(Base):
    __tablename__ = "identifiers"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        index=True,
        nullable=False,
    )

    chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    element_id: Mapped[str | None] = mapped_column(
        ForeignKey("elements.id"),
        nullable=True,
        index=True,
    )

    raw_value: Mapped[str] = mapped_column(String, nullable=False)
    normalized_value: Mapped[str] = mapped_column(String, nullable=False, index=True)
    identifier_type: Mapped[str] = mapped_column(String, nullable=False)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
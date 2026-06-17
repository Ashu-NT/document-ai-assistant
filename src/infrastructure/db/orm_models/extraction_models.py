from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class ExtractionResultORM(Base):
    __tablename__ = "extraction_results"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class MaintenanceTaskORM(Base):
    __tablename__ = "maintenance_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    extraction_id: Mapped[str | None] = mapped_column(
        ForeignKey("extraction_results.id"),
        nullable=True,
        index=True,
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    interval: Mapped[str | None] = mapped_column(String, nullable=True)

    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    equipment_id: Mapped[str | None] = mapped_column(String, nullable=True)

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SparePartORM(Base):
    __tablename__ = "spare_parts"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    extraction_id: Mapped[str | None] = mapped_column(
        ForeignKey("extraction_results.id"),
        nullable=True,
        index=True,
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    part_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[str | None] = mapped_column(String, nullable=True)

    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer_name: Mapped[str | None] = mapped_column(String, nullable=True)

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class EquipmentInfoORM(Base):
    __tablename__ = "equipment_info"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    extraction_id: Mapped[str | None] = mapped_column(
        ForeignKey("extraction_results.id"),
        nullable=True,
        index=True,
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    model_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    manufacturer_name: Mapped[str | None] = mapped_column(String, nullable=True)

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ManufacturerORM(Base):
    __tablename__ = "manufacturers"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    extraction_id: Mapped[str | None] = mapped_column(
        ForeignKey("extraction_results.id"),
        nullable=True,
        index=True,
    )

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True)

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
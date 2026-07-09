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
    source_chunk_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempted_chunk_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    unresolved_chunk_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ProcedureORM(Base):
    __tablename__ = "procedures"

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
    procedure_type: Mapped[str] = mapped_column(
        String, nullable=False, server_default="unknown", index=True
    )
    steps_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    equipment_id: Mapped[str | None] = mapped_column(
        ForeignKey("equipment_info.id"),
        nullable=True,
        index=True,
    )

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SpecificationORM(Base):
    __tablename__ = "specifications"

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

    parameter: Mapped[str] = mapped_column(String, nullable=False, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class TroubleshootingEntryORM(Base):
    __tablename__ = "troubleshooting_entries"

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

    symptom: Mapped[str] = mapped_column(Text, nullable=False)
    cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    remedy: Mapped[str | None] = mapped_column(Text, nullable=True)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    equipment_id: Mapped[str | None] = mapped_column(
        ForeignKey("equipment_info.id"),
        nullable=True,
        index=True,
    )

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SafetyWarningORM(Base):
    __tablename__ = "safety_warnings"

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

    warning_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class MaintenanceIntervalORM(Base):
    __tablename__ = "maintenance_intervals"

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

    interval: Mapped[str] = mapped_column(String, nullable=False)
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    maintenance_task_id: Mapped[str | None] = mapped_column(
        ForeignKey("maintenance_tasks.id"),
        nullable=True,
        index=True,
    )

    source_chunk_id: Mapped[str | None] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=True,
        index=True,
    )

    page_start: Mapped[int | None] = mapped_column(nullable=True)
    page_end: Mapped[int | None] = mapped_column(nullable=True)
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


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


class SupplierORM(Base):
    __tablename__ = "suppliers"

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
    source_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

import pytest

from src.domain.extraction import (
    ContactPoint,
    ContactPointType,
    EquipmentInfo,
    Manufacturer,
    MaintenanceInterval,
    MaintenanceTask,
    Procedure,
    SafetyWarning,
    SemanticSourceMetadata,
    SparePart,
    Specification,
    Supplier,
    SemanticEntityType,
    TroubleshootingEntry,
)

from src.infrastructure.db.mappers import (
    ContactPointMapper,
    EquipmentInfoMapper,
    ExtractionResultMapper,
    MaintenanceIntervalMapper,
    MaintenanceTaskMapper,
    ManufacturerMapper,
    ProcedureMapper,
    SafetyWarningMapper,
    SparePartMapper,
    SpecificationMapper,
    SupplierMapper,
    TroubleshootingEntryMapper,
)

_SAMPLE_SOURCE_METADATA = SemanticSourceMetadata(
    document_id="document_001",
    chunk_id="chunk_001",
    section_id="section_001",
    section_path=("4", "Maintenance"),
    page_start=4,
    page_end=5,
    parent_section_id="section_root",
    table_id="table_001",
    source_element_ids=("element_001",),
    nearby_chunk_ids=("chunk_000", "chunk_002"),
)

__all__ = [name for name in globals() if not name.startswith("__")]

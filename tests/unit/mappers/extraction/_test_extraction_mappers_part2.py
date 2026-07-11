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

def test_extraction_result_mapper_round_trip(
    sample_extraction_result,
    sample_contact_point,
) -> None:
    sample_extraction_result.contact_points = [sample_contact_point]
    result_orm = ExtractionResultMapper.to_orm(sample_extraction_result)

    task_rows = [
        MaintenanceTaskMapper.to_orm(
            task,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for task in sample_extraction_result.maintenance_tasks
    ]

    spare_part_rows = [
        SparePartMapper.to_orm(
            part,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for part in sample_extraction_result.spare_parts
    ]

    equipment_rows = [
        EquipmentInfoMapper.to_orm(
            equipment,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for equipment in sample_extraction_result.equipment
    ]

    manufacturer_rows = [
        ManufacturerMapper.to_orm(
            manufacturer,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for manufacturer in sample_extraction_result.manufacturers
    ]

    supplier_rows = [
        SupplierMapper.to_orm(
            supplier,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for supplier in sample_extraction_result.suppliers
    ]

    contact_point_rows = [
        ContactPointMapper.to_orm(
            contact_point,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for contact_point in sample_extraction_result.contact_points
    ]

    procedure_rows = [
        ProcedureMapper.to_orm(
            procedure,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for procedure in sample_extraction_result.procedures
    ]

    specification_rows = [
        SpecificationMapper.to_orm(
            specification,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for specification in sample_extraction_result.specifications
    ]

    safety_warning_rows = [
        SafetyWarningMapper.to_orm(
            safety_warning,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for safety_warning in sample_extraction_result.safety_warnings
    ]

    maintenance_interval_rows = [
        MaintenanceIntervalMapper.to_orm(
            maintenance_interval,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for maintenance_interval in sample_extraction_result.maintenance_intervals
    ]

    troubleshooting_entry_rows = [
        TroubleshootingEntryMapper.to_orm(
            troubleshooting_entry,
            extraction_id=sample_extraction_result.extraction_id,
        )
        for troubleshooting_entry in sample_extraction_result.troubleshooting_entries
    ]

    domain = ExtractionResultMapper.to_domain(
        result_orm,
        task_rows=task_rows,
        spare_part_rows=spare_part_rows,
        equipment_rows=equipment_rows,
        manufacturer_rows=manufacturer_rows,
        supplier_rows=supplier_rows,
        contact_point_rows=contact_point_rows,
        procedure_rows=procedure_rows,
        specification_rows=specification_rows,
        safety_warning_rows=safety_warning_rows,
        maintenance_interval_rows=maintenance_interval_rows,
        troubleshooting_entry_rows=troubleshooting_entry_rows,
    )

    assert domain.extraction_id == sample_extraction_result.extraction_id
    assert domain.task_count() == 1
    assert domain.spare_part_count() == 1
    assert len(domain.suppliers) == 1
    assert domain.suppliers[0].supplier_id == sample_extraction_result.suppliers[0].supplier_id
    assert len(domain.contact_points) == 1
    assert (
        domain.contact_points[0].contact_point_id
        == sample_extraction_result.contact_points[0].contact_point_id
    )
    assert len(domain.procedures) == 1
    assert domain.procedures[0].procedure_id == sample_extraction_result.procedures[0].procedure_id
    assert len(domain.specifications) == 1
    assert len(domain.safety_warnings) == 1
    assert len(domain.maintenance_intervals) == 1
    assert len(domain.troubleshooting_entries) == 1
    assert (
        domain.troubleshooting_entries[0].troubleshooting_id
        == sample_extraction_result.troubleshooting_entries[0].troubleshooting_id
    )

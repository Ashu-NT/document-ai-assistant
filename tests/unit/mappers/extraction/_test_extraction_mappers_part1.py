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

def test_source_metadata_round_trips_through_json_column(entity, mapper) -> None:
    orm = mapper.to_orm(entity, extraction_id="extraction_001")
    domain = mapper.to_domain(orm)

    assert domain.source_metadata == _SAMPLE_SOURCE_METADATA

def test_source_metadata_round_trips_as_none_when_absent(entity, mapper) -> None:
    orm = mapper.to_orm(entity, extraction_id="extraction_001")
    domain = mapper.to_domain(orm)

    assert domain.source_metadata is None

def test_maintenance_task_mapper_round_trip(sample_maintenance_task) -> None:
    orm = MaintenanceTaskMapper.to_orm(
        sample_maintenance_task,
        extraction_id="extraction_001",
    )
    domain = MaintenanceTaskMapper.to_domain(orm)

    assert domain.task_id == sample_maintenance_task.task_id
    assert domain.title == sample_maintenance_task.title
    assert domain.interval == sample_maintenance_task.interval

def test_spare_part_mapper_round_trip(sample_spare_part) -> None:
    orm = SparePartMapper.to_orm(
        sample_spare_part,
        extraction_id="extraction_001",
    )
    domain = SparePartMapper.to_domain(orm)

    assert domain.spare_part_id == sample_spare_part.spare_part_id
    assert domain.part_number == sample_spare_part.part_number

def test_equipment_info_mapper_round_trip(sample_equipment_info) -> None:
    orm = EquipmentInfoMapper.to_orm(
        sample_equipment_info,
        extraction_id="extraction_001",
    )
    domain = EquipmentInfoMapper.to_domain(orm)

    assert domain.equipment_id == sample_equipment_info.equipment_id
    assert domain.name == sample_equipment_info.name

def test_manufacturer_mapper_round_trip(sample_manufacturer) -> None:
    orm = ManufacturerMapper.to_orm(
        sample_manufacturer,
        extraction_id="extraction_001",
    )
    domain = ManufacturerMapper.to_domain(orm)

    assert domain.manufacturer_id == sample_manufacturer.manufacturer_id
    assert domain.name == sample_manufacturer.name

def test_supplier_mapper_round_trip(sample_supplier) -> None:
    orm = SupplierMapper.to_orm(
        sample_supplier,
        extraction_id="extraction_001",
    )
    domain = SupplierMapper.to_domain(orm)

    assert domain.supplier_id == sample_supplier.supplier_id
    assert domain.name == sample_supplier.name

def test_contact_point_mapper_round_trip(sample_contact_point) -> None:
    orm = ContactPointMapper.to_orm(
        sample_contact_point,
        extraction_id="extraction_001",
    )
    domain = ContactPointMapper.to_domain(orm)

    assert domain.contact_point_id == sample_contact_point.contact_point_id
    assert domain.value == sample_contact_point.value
    assert domain.owner_name == sample_contact_point.owner_name
    assert domain.owner_entity_type == sample_contact_point.owner_entity_type

def test_procedure_mapper_round_trip(sample_procedure) -> None:
    orm = ProcedureMapper.to_orm(
        sample_procedure,
        extraction_id="extraction_001",
    )
    domain = ProcedureMapper.to_domain(orm)

    assert domain.procedure_id == sample_procedure.procedure_id
    assert domain.title == sample_procedure.title
    assert domain.procedure_type == sample_procedure.procedure_type
    assert domain.steps == sample_procedure.steps
    assert domain.equipment_id == sample_procedure.equipment_id

def test_specification_mapper_round_trip(sample_specification) -> None:
    orm = SpecificationMapper.to_orm(
        sample_specification,
        extraction_id="extraction_001",
    )
    domain = SpecificationMapper.to_domain(orm)

    assert domain.specification_id == sample_specification.specification_id
    assert domain.parameter == sample_specification.parameter
    assert domain.value == sample_specification.value
    assert domain.unit == sample_specification.unit

def test_safety_warning_mapper_round_trip(sample_safety_warning) -> None:
    orm = SafetyWarningMapper.to_orm(
        sample_safety_warning,
        extraction_id="extraction_001",
    )
    domain = SafetyWarningMapper.to_domain(orm)

    assert domain.safety_warning_id == sample_safety_warning.safety_warning_id
    assert domain.warning_type == sample_safety_warning.warning_type
    assert domain.message == sample_safety_warning.message

def test_maintenance_interval_mapper_round_trip(sample_maintenance_interval) -> None:
    orm = MaintenanceIntervalMapper.to_orm(
        sample_maintenance_interval,
        extraction_id="extraction_001",
    )
    domain = MaintenanceIntervalMapper.to_domain(orm)

    assert domain.maintenance_interval_id == sample_maintenance_interval.maintenance_interval_id
    assert domain.interval == sample_maintenance_interval.interval
    assert domain.maintenance_task_id == sample_maintenance_interval.maintenance_task_id

def test_troubleshooting_entry_mapper_round_trip(sample_troubleshooting_entry) -> None:
    orm = TroubleshootingEntryMapper.to_orm(
        sample_troubleshooting_entry,
        extraction_id="extraction_001",
    )
    domain = TroubleshootingEntryMapper.to_domain(orm)

    assert domain.troubleshooting_id == sample_troubleshooting_entry.troubleshooting_id
    assert domain.symptom == sample_troubleshooting_entry.symptom
    assert domain.cause == sample_troubleshooting_entry.cause
    assert domain.remedy == sample_troubleshooting_entry.remedy
    assert domain.equipment_id == sample_troubleshooting_entry.equipment_id

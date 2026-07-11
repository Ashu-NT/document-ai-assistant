from tests.unit.mappers.extraction._test_extraction_mappers_support import *  # noqa: F401,F403

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

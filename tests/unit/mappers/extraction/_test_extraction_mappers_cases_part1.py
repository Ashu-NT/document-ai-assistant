from tests.unit.mappers.extraction._test_extraction_mappers_support import *  # noqa: F401,F403

@pytest.mark.parametrize(
    "entity, mapper",
    [
        (
            MaintenanceTask(
                task_id="task_001",
                document_id="document_001",
                title="Replace hydraulic filter",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            MaintenanceTaskMapper,
        ),
        (
            SparePart(
                spare_part_id="spare_001",
                document_id="document_001",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            SparePartMapper,
        ),
        (
            ContactPoint(
                contact_point_id="contact_point_001",
                document_id="document_001",
                contact_type=ContactPointType.EMAIL_ADDRESS,
                value="service@example.com",
                owner_name="Example Manufacturer",
                owner_entity_type=SemanticEntityType.MANUFACTURER,
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            ContactPointMapper,
        ),
        (
            EquipmentInfo(
                equipment_id="equipment_001",
                document_id="document_001",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            EquipmentInfoMapper,
        ),
        (
            Manufacturer(
                manufacturer_id="manufacturer_001",
                document_id="document_001",
                name="Example Manufacturer",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            ManufacturerMapper,
        ),
        (
            Procedure(
                procedure_id="procedure_001",
                document_id="document_001",
                title="Install hydraulic filter",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            ProcedureMapper,
        ),
        (
            SafetyWarning(
                safety_warning_id="safety_warning_001",
                document_id="document_001",
                warning_type="warning",
                message="Depressurize before servicing.",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            SafetyWarningMapper,
        ),
        (
            MaintenanceInterval(
                maintenance_interval_id="maintenance_interval_001",
                document_id="document_001",
                interval="1000 operating hours",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            MaintenanceIntervalMapper,
        ),
        (
            Specification(
                specification_id="specification_001",
                document_id="document_001",
                parameter="Pressure rating",
                value="16",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            SpecificationMapper,
        ),
        (
            Supplier(
                supplier_id="supplier_001",
                document_id="document_001",
                name="Example Supplier",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            SupplierMapper,
        ),
        (
            TroubleshootingEntry(
                troubleshooting_id="troubleshooting_001",
                document_id="document_001",
                symptom="Pump fails to build pressure",
                source_metadata=_SAMPLE_SOURCE_METADATA,
            ),
            TroubleshootingEntryMapper,
        ),
    ],
)
def test_source_metadata_round_trips_through_json_column(entity, mapper) -> None:
    orm = mapper.to_orm(entity, extraction_id="extraction_001")
    domain = mapper.to_domain(orm)

    assert domain.source_metadata == _SAMPLE_SOURCE_METADATA

@pytest.mark.parametrize(
    "entity, mapper",
    [
        (
            MaintenanceTask(
                task_id="task_001", document_id="document_001", title="Task"
            ),
            MaintenanceTaskMapper,
        ),
        (SparePart(spare_part_id="spare_001", document_id="document_001"), SparePartMapper),
        (
            EquipmentInfo(equipment_id="equipment_001", document_id="document_001"),
            EquipmentInfoMapper,
        ),
        (
            Manufacturer(
                manufacturer_id="manufacturer_001",
                document_id="document_001",
                name="Example Manufacturer",
            ),
            ManufacturerMapper,
        ),
        (
            Procedure(
                procedure_id="procedure_001", document_id="document_001", title="Procedure"
            ),
            ProcedureMapper,
        ),
        (
            SafetyWarning(
                safety_warning_id="safety_warning_001",
                document_id="document_001",
                warning_type="warning",
                message="Warning message.",
            ),
            SafetyWarningMapper,
        ),
        (
            MaintenanceInterval(
                maintenance_interval_id="maintenance_interval_001",
                document_id="document_001",
                interval="1000 operating hours",
            ),
            MaintenanceIntervalMapper,
        ),
        (
            Specification(
                specification_id="specification_001",
                document_id="document_001",
                parameter="Pressure rating",
                value="16",
            ),
            SpecificationMapper,
        ),
        (
            Supplier(
                supplier_id="supplier_001",
                document_id="document_001",
                name="Example Supplier",
            ),
            SupplierMapper,
        ),
        (
            TroubleshootingEntry(
                troubleshooting_id="troubleshooting_001",
                document_id="document_001",
                symptom="Pump fails to build pressure",
            ),
            TroubleshootingEntryMapper,
        ),
    ],
)
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

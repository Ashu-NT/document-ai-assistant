import pytest

from src.domain.extraction import (
    ContactPoint,
    ContactPointType,
    EquipmentInfo,
    ExtractionResult,
    MaintenanceInterval,
    MaintenanceTask,
    Manufacturer,
    Procedure,
    ProcedureType,
    SafetyWarning,
    SemanticEntityType,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)


@pytest.fixture
def sample_maintenance_task(document_id: str, chunk_id: str) -> MaintenanceTask:
    return MaintenanceTask(
        task_id="task_001",
        document_id=document_id,
        title="Replace hydraulic filter",
        interval="1000 operating hours",
        component_name="Hydraulic filter",
        source_chunk_id=chunk_id,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_spare_part(document_id: str, chunk_id: str) -> SparePart:
    return SparePart(
        spare_part_id="spare_001",
        document_id=document_id,
        part_number="HP-001",
        description="Hydraulic filter",
        quantity="1",
        source_chunk_id=chunk_id,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_equipment_info(document_id: str, chunk_id: str) -> EquipmentInfo:
    return EquipmentInfo(
        equipment_id="equipment_001",
        document_id=document_id,
        name="Hydraulic Pump",
        model_number="HP-500",
        manufacturer_name="Example Manufacturer",
        source_chunk_id=chunk_id,
        confidence_score=0.85,
    )


@pytest.fixture
def sample_manufacturer(document_id: str, chunk_id: str) -> Manufacturer:
    return Manufacturer(
        manufacturer_id="manufacturer_001",
        document_id=document_id,
        name="Example Manufacturer",
        source_chunk_id=chunk_id,
        confidence_score=0.85,
    )


@pytest.fixture
def sample_supplier(document_id: str, chunk_id: str) -> Supplier:
    return Supplier(
        supplier_id="supplier_001",
        document_id=document_id,
        name="Example Supplier",
        source_chunk_id=chunk_id,
        confidence_score=0.85,
    )


@pytest.fixture
def sample_contact_point(document_id: str, chunk_id: str) -> ContactPoint:
    return ContactPoint(
        contact_point_id="contact_point_001",
        document_id=document_id,
        contact_type=ContactPointType.EMAIL_ADDRESS,
        value="service@example.com",
        label="service",
        owner_name="Example Manufacturer",
        owner_entity_type=SemanticEntityType.MANUFACTURER,
        source_chunk_id=chunk_id,
        confidence_score=0.85,
    )


@pytest.fixture
def sample_procedure(
    document_id: str,
    chunk_id: str,
    sample_equipment_info: EquipmentInfo,
) -> Procedure:
    return Procedure(
        procedure_id="procedure_001",
        document_id=document_id,
        title="Install hydraulic filter",
        procedure_type=ProcedureType.INSTALLATION,
        steps=[
            "Depressurize the line.",
            "Remove the old filter.",
            "Install the new filter.",
        ],
        component_name="Hydraulic filter",
        equipment_id=sample_equipment_info.equipment_id,
        source_chunk_id=chunk_id,
        confidence_score=0.85,
    )


@pytest.fixture
def sample_specification(document_id: str, chunk_id: str) -> Specification:
    return Specification(
        specification_id="specification_001",
        document_id=document_id,
        parameter="Pressure rating",
        value="16",
        unit="bar",
        component_name="Hydraulic pump",
        source_chunk_id=chunk_id,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_safety_warning(document_id: str, chunk_id: str) -> SafetyWarning:
    return SafetyWarning(
        safety_warning_id="safety_warning_001",
        document_id=document_id,
        warning_type="danger",
        message="Depressurize the hydraulic line before removing the filter housing.",
        component_name="Hydraulic filter",
        source_chunk_id=chunk_id,
        confidence_score=0.93,
    )


@pytest.fixture
def sample_maintenance_interval(
    document_id: str,
    chunk_id: str,
    sample_maintenance_task: MaintenanceTask,
) -> MaintenanceInterval:
    return MaintenanceInterval(
        maintenance_interval_id="maintenance_interval_001",
        document_id=document_id,
        interval="1000 operating hours",
        component_name="Hydraulic filter",
        maintenance_task_id=sample_maintenance_task.task_id,
        source_chunk_id=chunk_id,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_troubleshooting_entry(
    document_id: str,
    chunk_id: str,
    sample_equipment_info: EquipmentInfo,
) -> TroubleshootingEntry:
    return TroubleshootingEntry(
        troubleshooting_id="troubleshooting_001",
        document_id=document_id,
        symptom="Pump fails to build pressure",
        cause="Worn hydraulic filter",
        remedy="Replace the hydraulic filter",
        component_name="Hydraulic filter",
        equipment_id=sample_equipment_info.equipment_id,
        source_chunk_id=chunk_id,
        confidence_score=0.9,
    )


@pytest.fixture
def sample_extraction_result(
    document_id: str,
    sample_maintenance_task: MaintenanceTask,
    sample_spare_part: SparePart,
    sample_equipment_info: EquipmentInfo,
    sample_manufacturer: Manufacturer,
    sample_supplier: Supplier,
    sample_procedure: Procedure,
    sample_specification: Specification,
    sample_safety_warning: SafetyWarning,
    sample_maintenance_interval: MaintenanceInterval,
    sample_troubleshooting_entry: TroubleshootingEntry,
) -> ExtractionResult:
    return ExtractionResult(
        extraction_id="extraction_001",
        document_id=document_id,
        maintenance_tasks=[sample_maintenance_task],
        spare_parts=[sample_spare_part],
        equipment=[sample_equipment_info],
        manufacturers=[sample_manufacturer],
        suppliers=[sample_supplier],
        procedures=[sample_procedure],
        specifications=[sample_specification],
        safety_warnings=[sample_safety_warning],
        maintenance_intervals=[sample_maintenance_interval],
        troubleshooting_entries=[sample_troubleshooting_entry],
        confidence_score=0.88,
    )

from src.application.workflows.linking import SemanticLinkingWorkflow
from src.domain.extraction import (
    ContactPoint,
    ContactPointType,
    EquipmentInfo,
    Manufacturer,
    MaintenanceInterval,
    MaintenanceTask,
    Procedure,
    SafetyWarning,
    SemanticEntityType,
    SemanticRelationshipStatus,
    SemanticRelationshipType,
    SemanticSourceMetadata,
    SparePart,
    Specification,
    Supplier,
    TroubleshootingEntry,
)
from src.shared.ids import IdGenerator


class FakeExtractionService:
    def __init__(self, *, document_id: str, **entities) -> None:
        self.document_id = document_id
        self._entities = {
            "maintenance_tasks": [],
            "maintenance_intervals": [],
            "procedures": [],
            "spare_parts": [],
            "safety_warnings": [],
            "equipment": [],
            "manufacturers": [],
            "suppliers": [],
            "contact_points": [],
            "specifications": [],
            "troubleshooting_entries": [],
        }
        self._entities.update(entities)
        self.replaced: list[tuple[str, list]] = []

    def list_maintenance_tasks(self, document_id):
        return self._entities["maintenance_tasks"]

    def list_maintenance_intervals(self, document_id):
        return self._entities["maintenance_intervals"]

    def list_procedures(self, document_id):
        return self._entities["procedures"]

    def list_spare_parts(self, document_id):
        return self._entities["spare_parts"]

    def list_safety_warnings(self, document_id):
        return self._entities["safety_warnings"]

    def list_equipment(self, document_id):
        return self._entities["equipment"]

    def list_manufacturers(self, document_id):
        return self._entities["manufacturers"]

    def list_suppliers(self, document_id):
        return self._entities["suppliers"]

    def list_contact_points(self, document_id):
        return self._entities["contact_points"]

    def list_specifications(self, document_id):
        return self._entities["specifications"]

    def list_troubleshooting_entries(self, document_id):
        return self._entities["troubleshooting_entries"]

    def replace_semantic_relationships(self, document_id, relationships):
        self.replaced.append((document_id, relationships))


def _metadata(chunk_id: str, **overrides) -> SemanticSourceMetadata:
    defaults = {"document_id": "document_001", "chunk_id": chunk_id}
    defaults.update(overrides)
    return SemanticSourceMetadata(**defaults)


def test_link_persists_fk_passthrough_and_proximity_relationships() -> None:
    task = MaintenanceTask(
        task_id="task_001",
        document_id="document_001",
        title="Replace hydraulic filter",
        source_metadata=_metadata("chunk_001"),
    )
    procedure = Procedure(
        procedure_id="procedure_001",
        document_id="document_001",
        title="Filter replacement procedure",
        source_metadata=_metadata("chunk_001"),
    )
    interval = MaintenanceInterval(
        maintenance_interval_id="interval_001",
        document_id="document_001",
        interval="1000 hours",
        maintenance_task_id="task_001",
    )
    equipment = EquipmentInfo(equipment_id="equipment_001", document_id="document_001")
    troubleshooting_entry = TroubleshootingEntry(
        troubleshooting_id="troubleshooting_001",
        document_id="document_001",
        symptom="Pump fails to build pressure",
        equipment_id="equipment_001",
    )

    service = FakeExtractionService(
        document_id="document_001",
        maintenance_tasks=[task],
        maintenance_intervals=[interval],
        procedures=[procedure],
        equipment=[equipment],
        troubleshooting_entries=[troubleshooting_entry],
    )
    workflow = SemanticLinkingWorkflow(
        extraction_service=service, id_generator=IdGenerator()
    )

    relationships = workflow.link("document_001")

    relationship_types = {r.relationship_type for r in relationships}
    assert relationship_types == {
        SemanticRelationshipType.TASK_HAS_INTERVAL,
        SemanticRelationshipType.EQUIPMENT_HAS_TROUBLESHOOTING_ENTRY,
        SemanticRelationshipType.TASK_USES_PROCEDURE,
    }

    fk_relationships = [
        r
        for r in relationships
        if r.relationship_type
        in (
            SemanticRelationshipType.TASK_HAS_INTERVAL,
            SemanticRelationshipType.EQUIPMENT_HAS_TROUBLESHOOTING_ENTRY,
        )
    ]
    for relationship in fk_relationships:
        assert relationship.confidence_score == 1.0
        assert relationship.status == SemanticRelationshipStatus.ACCEPTED
        assert relationship.evidence == "existing_fk"

    task_uses_procedure = next(
        r
        for r in relationships
        if r.relationship_type == SemanticRelationshipType.TASK_USES_PROCEDURE
    )
    assert task_uses_procedure.source_entity_type == SemanticEntityType.MAINTENANCE_TASK
    assert task_uses_procedure.source_entity_id == "task_001"
    assert task_uses_procedure.target_entity_type == SemanticEntityType.PROCEDURE
    assert task_uses_procedure.target_entity_id == "procedure_001"
    assert task_uses_procedure.status == SemanticRelationshipStatus.ACCEPTED

    assert service.replaced == [("document_001", relationships)]
    for relationship in relationships:
        assert relationship.document_id == "document_001"
        assert relationship.relationship_id


def test_link_produces_no_relationships_when_entities_share_no_window() -> None:
    task = MaintenanceTask(
        task_id="task_001",
        document_id="document_001",
        title="Replace hydraulic filter",
        source_metadata=_metadata("chunk_001", page_start=1),
    )
    spare_part = SparePart(
        spare_part_id="spare_001",
        document_id="document_001",
        source_metadata=_metadata("chunk_099", page_start=50),
    )

    service = FakeExtractionService(
        document_id="document_001",
        maintenance_tasks=[task],
        spare_parts=[spare_part],
    )
    workflow = SemanticLinkingWorkflow(
        extraction_service=service, id_generator=IdGenerator()
    )

    relationships = workflow.link("document_001")

    assert relationships == []


def test_link_ignores_entities_without_source_metadata() -> None:
    task = MaintenanceTask(
        task_id="task_001",
        document_id="document_001",
        title="Replace hydraulic filter",
        source_metadata=None,
    )
    safety_warning = SafetyWarning(
        safety_warning_id="warning_001",
        document_id="document_001",
        warning_type="hazard",
        message="Depressurize before servicing",
        source_metadata=None,
    )

    service = FakeExtractionService(
        document_id="document_001",
        maintenance_tasks=[task],
        safety_warnings=[safety_warning],
    )
    workflow = SemanticLinkingWorkflow(
        extraction_service=service, id_generator=IdGenerator()
    )

    relationships = workflow.link("document_001")

    assert relationships == []


def test_link_covers_equipment_spare_part_and_specification_pairs() -> None:
    equipment = EquipmentInfo(
        equipment_id="equipment_001",
        document_id="document_001",
        source_metadata=_metadata("chunk_001"),
    )
    spare_part = SparePart(
        spare_part_id="spare_001",
        document_id="document_001",
        source_metadata=_metadata("chunk_001"),
    )
    specification = Specification(
        specification_id="specification_001",
        document_id="document_001",
        parameter="Pressure rating",
        value="200 bar",
        source_metadata=_metadata("chunk_001"),
    )

    service = FakeExtractionService(
        document_id="document_001",
        equipment=[equipment],
        spare_parts=[spare_part],
        specifications=[specification],
    )
    workflow = SemanticLinkingWorkflow(
        extraction_service=service, id_generator=IdGenerator()
    )

    relationships = workflow.link("document_001")

    relationship_types = {r.relationship_type for r in relationships}
    assert relationship_types == {
        SemanticRelationshipType.EQUIPMENT_HAS_SPARE_PART,
        SemanticRelationshipType.EQUIPMENT_HAS_SPECIFICATION,
    }
    for relationship in relationships:
        assert relationship.source_entity_type == SemanticEntityType.EQUIPMENT
        assert relationship.source_entity_id == "equipment_001"


def test_link_attaches_contact_points_to_manufacturer_by_owner_reference() -> None:
    manufacturer = Manufacturer(
        manufacturer_id="manufacturer_001",
        document_id="document_001",
        name="ACME Corp",
    )
    contact_point = ContactPoint(
        contact_point_id="contact_point_001",
        document_id="document_001",
        contact_type=ContactPointType.EMAIL_ADDRESS,
        value="service@acme.example",
        owner_name="ACME Corp",
        owner_entity_type=SemanticEntityType.MANUFACTURER,
    )
    service = FakeExtractionService(
        document_id="document_001",
        manufacturers=[manufacturer],
        contact_points=[contact_point],
    )
    workflow = SemanticLinkingWorkflow(
        extraction_service=service, id_generator=IdGenerator()
    )

    relationships = workflow.link("document_001")

    assert len(relationships) == 1
    relationship = relationships[0]
    assert (
        relationship.relationship_type
        == SemanticRelationshipType.MANUFACTURER_HAS_CONTACT_POINT
    )
    assert relationship.source_entity_type == SemanticEntityType.MANUFACTURER
    assert relationship.source_entity_id == "manufacturer_001"
    assert relationship.target_entity_type == SemanticEntityType.CONTACT_POINT
    assert relationship.target_entity_id == "contact_point_001"
    assert relationship.status == SemanticRelationshipStatus.ACCEPTED
    assert relationship.evidence == "owner_reference_exact"

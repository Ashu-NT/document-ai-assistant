from src.application.workflows.linking.semantic_entity_index import (
    IndexedEntity,
    SemanticEntityIndex,
)

from src.application.workflows.linking.semantic_relationship_candidate_generator import (
    EVIDENCE_EXISTING_FK,
    EVIDENCE_NEARBY_CHUNK,
    EVIDENCE_NEARBY_PAGE,
    EVIDENCE_SAME_CHUNK,
    EVIDENCE_SAME_PARENT_SECTION,
    EVIDENCE_SAME_SECTION,
    EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY,
    SemanticRelationshipCandidateGenerator,
    generate_fk_passthrough_candidates,
)

from src.domain.extraction import (
    EquipmentInfo,
    MaintenanceInterval,
    MaintenanceTask,
    Procedure,
    SemanticEntityType,
    SemanticRelationshipType,
    TroubleshootingEntry,
)

def _entity(entity_type, entity_id, **overrides) -> IndexedEntity:
    defaults = {
        "chunk_id": None,
        "section_id": None,
        "parent_section_id": None,
        "table_id": None,
        "page_start": None,
        "nearby_chunk_ids": (),
    }
    defaults.update(overrides)
    return IndexedEntity(entity_type=entity_type, entity_id=entity_id, **defaults)

def _generate(entities):
    return SemanticRelationshipCandidateGenerator().generate(SemanticEntityIndex(entities))

def test_fk_passthrough_equipment_has_procedure_and_troubleshooting_entry() -> None:
    equipment = EquipmentInfo(equipment_id="equipment_001", document_id="document_001")
    procedure = Procedure(
        procedure_id="procedure_001",
        document_id="document_001",
        title="Replace filter",
        equipment_id="equipment_001",
    )
    troubleshooting_entry = TroubleshootingEntry(
        troubleshooting_id="troubleshooting_001",
        document_id="document_001",
        symptom="Pump fails to build pressure",
        equipment_id="equipment_001",
    )

    candidates = generate_fk_passthrough_candidates(
        maintenance_tasks=[],
        maintenance_intervals=[],
        equipment=[equipment],
        procedures=[procedure],
        troubleshooting_entries=[troubleshooting_entry],
    )

    relationship_types = {candidate.relationship_type for candidate in candidates}
    assert relationship_types == {
        SemanticRelationshipType.EQUIPMENT_HAS_PROCEDURE,
        SemanticRelationshipType.EQUIPMENT_HAS_TROUBLESHOOTING_ENTRY,
    }
    for candidate in candidates:
        assert candidate.source_entity_id == "equipment_001"
        assert candidate.evidence == EVIDENCE_EXISTING_FK

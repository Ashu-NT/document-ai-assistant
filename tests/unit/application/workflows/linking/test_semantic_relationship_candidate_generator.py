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


def test_same_chunk_generates_candidate_for_allow_listed_pair() -> None:
    task = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_001", chunk_id="chunk_001")
    procedure = _entity(
        SemanticEntityType.PROCEDURE, "procedure_001", chunk_id="chunk_001"
    )

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.relationship_type == SemanticRelationshipType.TASK_USES_PROCEDURE
    assert candidate.source_entity_id == "task_001"
    assert candidate.target_entity_id == "procedure_001"
    assert candidate.evidence == EVIDENCE_SAME_CHUNK


def test_direction_is_fixed_by_pair_definition_regardless_of_argument_order() -> None:
    procedure = _entity(
        SemanticEntityType.PROCEDURE, "procedure_001", chunk_id="chunk_001"
    )
    task = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_001", chunk_id="chunk_001")

    candidates = _generate([procedure, task])

    assert len(candidates) == 1
    assert candidates[0].source_entity_type == SemanticEntityType.MAINTENANCE_TASK
    assert candidates[0].target_entity_type == SemanticEntityType.PROCEDURE


def test_non_allow_listed_pair_generates_no_candidate() -> None:
    task_a = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_001", chunk_id="chunk_001")
    task_b = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_002", chunk_id="chunk_001")

    candidates = _generate([task_a, task_b])

    assert candidates == []


def test_same_table_alone_does_not_generate_a_candidate() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        table_id="table_001",
        chunk_id="chunk_001",
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        table_id="table_001",
        chunk_id="chunk_002",
    )

    candidates = _generate([task, procedure])

    assert candidates == []


def test_same_table_with_chunk_proximity_outranks_same_chunk_alone() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        table_id="table_001",
        chunk_id="chunk_001",
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        table_id="table_001",
        chunk_id="chunk_001",
    )

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    assert candidates[0].evidence == EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY


def test_same_table_with_nearby_chunk_also_counts_as_proximity() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        table_id="table_001",
        chunk_id="chunk_001",
        nearby_chunk_ids=("chunk_002",),
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        table_id="table_001",
        chunk_id="chunk_002",
    )

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    assert candidates[0].evidence == EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY


def test_same_section_generates_candidate_when_chunks_differ() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        chunk_id="chunk_001",
        section_id="section_001",
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        chunk_id="chunk_002",
        section_id="section_001",
    )

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    assert candidates[0].evidence == EVIDENCE_SAME_SECTION


def test_nearby_chunk_generates_candidate() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        chunk_id="chunk_001",
        nearby_chunk_ids=("chunk_002",),
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        chunk_id="chunk_002",
    )

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    assert candidates[0].evidence == EVIDENCE_NEARBY_CHUNK


def test_same_parent_section_generates_candidate_when_section_differs() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        section_id="section_a",
        parent_section_id="section_root",
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        section_id="section_b",
        parent_section_id="section_root",
    )

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    assert candidates[0].evidence == EVIDENCE_SAME_PARENT_SECTION


def test_nearby_page_within_window_generates_candidate() -> None:
    task = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_001", page_start=2)
    procedure = _entity(SemanticEntityType.PROCEDURE, "procedure_001", page_start=3)

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    assert candidates[0].evidence == EVIDENCE_NEARBY_PAGE


def test_pages_outside_window_generate_no_candidate() -> None:
    task = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_001", page_start=2)
    procedure = _entity(SemanticEntityType.PROCEDURE, "procedure_001", page_start=5)

    candidates = _generate([task, procedure])

    assert candidates == []


def test_best_evidence_wins_when_multiple_windows_match() -> None:
    task = _entity(
        SemanticEntityType.MAINTENANCE_TASK,
        "task_001",
        chunk_id="chunk_001",
        section_id="section_001",
        page_start=1,
    )
    procedure = _entity(
        SemanticEntityType.PROCEDURE,
        "procedure_001",
        chunk_id="chunk_001",
        section_id="section_001",
        page_start=1,
    )

    candidates = _generate([task, procedure])

    assert len(candidates) == 1
    assert candidates[0].evidence == EVIDENCE_SAME_CHUNK


def test_fk_passthrough_task_has_interval() -> None:
    task = MaintenanceTask(task_id="task_001", document_id="document_001", title="Task")
    interval = MaintenanceInterval(
        maintenance_interval_id="interval_001",
        document_id="document_001",
        interval="1000 hours",
        maintenance_task_id="task_001",
    )

    candidates = generate_fk_passthrough_candidates(
        maintenance_tasks=[task],
        maintenance_intervals=[interval],
        equipment=[],
        procedures=[],
        troubleshooting_entries=[],
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.relationship_type == SemanticRelationshipType.TASK_HAS_INTERVAL
    assert candidate.source_entity_id == "task_001"
    assert candidate.target_entity_id == "interval_001"
    assert candidate.evidence == EVIDENCE_EXISTING_FK
    assert candidate.score == 1.0


def test_fk_passthrough_skips_unresolved_task_reference() -> None:
    interval = MaintenanceInterval(
        maintenance_interval_id="interval_001",
        document_id="document_001",
        interval="1000 hours",
        maintenance_task_id="task_missing",
    )

    candidates = generate_fk_passthrough_candidates(
        maintenance_tasks=[],
        maintenance_intervals=[interval],
        equipment=[],
        procedures=[],
        troubleshooting_entries=[],
    )

    assert candidates == []


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

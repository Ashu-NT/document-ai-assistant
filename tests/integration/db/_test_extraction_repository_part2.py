def test_list_safety_warnings(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    safety_warnings = db_uow.extractions.list_safety_warnings(
        sample_extraction_result.document_id
    )

    assert len(safety_warnings) == 1

def test_list_maintenance_intervals(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    maintenance_intervals = db_uow.extractions.list_maintenance_intervals(
        sample_extraction_result.document_id
    )

    assert len(maintenance_intervals) == 1

def test_search_procedures(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_procedures("Install hydraulic filter")
    no_matches = db_uow.extractions.search_procedures("Nonexistent Procedure")

    assert len(matches) == 1
    assert no_matches == []

def test_search_specifications(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_specifications("Pressure rating")
    no_matches = db_uow.extractions.search_specifications("Nonexistent Parameter")

    assert len(matches) == 1
    assert no_matches == []

def test_search_safety_warnings(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_safety_warnings("Depressurize")
    no_matches = db_uow.extractions.search_safety_warnings("Nonexistent Warning")

    assert len(matches) == 1
    assert no_matches == []

def test_search_maintenance_intervals(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_maintenance_intervals("1000 operating hours")
    no_matches = db_uow.extractions.search_maintenance_intervals("Nonexistent Interval")

    assert len(matches) == 1
    assert no_matches == []

def test_list_maintenance_intervals_by_task_id(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    task_id = sample_extraction_result.maintenance_tasks[0].task_id
    intervals = db_uow.extractions.list_maintenance_intervals_by_task_id(task_id)
    no_intervals = db_uow.extractions.list_maintenance_intervals_by_task_id("no_such_task")

    assert len(intervals) == 1
    assert intervals[0].maintenance_task_id == task_id
    assert no_intervals == []

def test_list_procedures_by_equipment_id(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    equipment_id = sample_extraction_result.equipment[0].equipment_id
    procedures = db_uow.extractions.list_procedures_by_equipment_id(equipment_id)
    no_procedures = db_uow.extractions.list_procedures_by_equipment_id("no_such_equipment")

    assert len(procedures) == 1
    assert procedures[0].equipment_id == equipment_id
    assert no_procedures == []

def test_list_troubleshooting_entries(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    troubleshooting_entries = db_uow.extractions.list_troubleshooting_entries(
        sample_extraction_result.document_id
    )

    assert len(troubleshooting_entries) == 1

def test_search_troubleshooting_entries(db_uow, sample_extraction_result) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    matches = db_uow.extractions.search_troubleshooting_entries(
        "Pump fails to build pressure"
    )
    no_matches = db_uow.extractions.search_troubleshooting_entries(
        "Nonexistent Symptom"
    )

    assert len(matches) == 1
    assert no_matches == []

def test_list_troubleshooting_entries_by_equipment_id(
    db_uow, sample_extraction_result
) -> None:
    db_uow.extractions.save_extraction_result(sample_extraction_result)
    db_uow.commit()

    equipment_id = sample_extraction_result.equipment[0].equipment_id
    entries = db_uow.extractions.list_troubleshooting_entries_by_equipment_id(
        equipment_id
    )
    no_entries = db_uow.extractions.list_troubleshooting_entries_by_equipment_id(
        "no_such_equipment"
    )

    assert len(entries) == 1
    assert entries[0].equipment_id == equipment_id
    assert no_entries == []

def test_replace_semantic_relationships_saves_and_lists_by_document(
    db_uow, document_id
) -> None:
    from src.domain.extraction import (
        SemanticEntityType,
        SemanticRelationship,
        SemanticRelationshipStatus,
        SemanticRelationshipType,
    )

    relationship = SemanticRelationship(
        relationship_id="semantic_relationship_001",
        document_id=document_id,
        relationship_type=SemanticRelationshipType.TASK_USES_PROCEDURE,
        source_entity_type=SemanticEntityType.MAINTENANCE_TASK,
        source_entity_id="task_001",
        target_entity_type=SemanticEntityType.PROCEDURE,
        target_entity_id="procedure_001",
        confidence_score=0.8,
        status=SemanticRelationshipStatus.ACCEPTED,
        evidence="same_chunk",
    )

    db_uow.extractions.replace_semantic_relationships(document_id, [relationship])
    db_uow.commit()

    loaded = db_uow.extractions.list_semantic_relationships(document_id)

    assert len(loaded) == 1
    assert loaded[0].relationship_id == "semantic_relationship_001"
    assert loaded[0].relationship_type == SemanticRelationshipType.TASK_USES_PROCEDURE
    assert loaded[0].source_entity_type == SemanticEntityType.MAINTENANCE_TASK
    assert loaded[0].status == SemanticRelationshipStatus.ACCEPTED
    assert loaded[0].confidence_score == 0.8
    assert loaded[0].evidence == "same_chunk"

    assert db_uow.extractions.list_semantic_relationships("no_such_document") == []

def test_replace_semantic_relationships_is_idempotent_for_document(
    db_uow, document_id
) -> None:
    from src.domain.extraction import (
        SemanticEntityType,
        SemanticRelationship,
        SemanticRelationshipStatus,
        SemanticRelationshipType,
    )

    first_run = SemanticRelationship(
        relationship_id="semantic_relationship_001",
        document_id=document_id,
        relationship_type=SemanticRelationshipType.TASK_HAS_INTERVAL,
        source_entity_type=SemanticEntityType.MAINTENANCE_TASK,
        source_entity_id="task_001",
        target_entity_type=SemanticEntityType.MAINTENANCE_INTERVAL,
        target_entity_id="interval_001",
        confidence_score=1.0,
        status=SemanticRelationshipStatus.ACCEPTED,
        evidence="existing_fk",
    )
    db_uow.extractions.replace_semantic_relationships(document_id, [first_run])
    db_uow.commit()

    second_run = SemanticRelationship(
        relationship_id="semantic_relationship_002",
        document_id=document_id,
        relationship_type=SemanticRelationshipType.TASK_USES_PROCEDURE,
        source_entity_type=SemanticEntityType.MAINTENANCE_TASK,
        source_entity_id="task_001",
        target_entity_type=SemanticEntityType.PROCEDURE,
        target_entity_id="procedure_001",
        confidence_score=0.8,
        status=SemanticRelationshipStatus.ACCEPTED,
        evidence="same_chunk",
    )
    db_uow.extractions.replace_semantic_relationships(document_id, [second_run])
    db_uow.commit()

    loaded = db_uow.extractions.list_semantic_relationships(document_id)

    assert len(loaded) == 1
    assert loaded[0].relationship_id == "semantic_relationship_002"

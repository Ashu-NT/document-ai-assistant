from src.domain.extraction import (
    SemanticEntityType,
    SemanticRelationship,
    SemanticRelationshipStatus,
    SemanticRelationshipType,
)


def _make(**overrides) -> SemanticRelationship:
    defaults = {
        "relationship_id": "semantic_relationship_001",
        "document_id": "document_001",
        "relationship_type": SemanticRelationshipType.TASK_USES_PROCEDURE,
        "source_entity_type": SemanticEntityType.MAINTENANCE_TASK,
        "source_entity_id": "task_001",
        "target_entity_type": SemanticEntityType.PROCEDURE,
        "target_entity_id": "procedure_001",
        "confidence_score": 0.8,
    }
    defaults.update(overrides)
    return SemanticRelationship(**defaults)


def test_defaults_to_needs_review_status() -> None:
    relationship = _make()

    assert relationship.status == SemanticRelationshipStatus.NEEDS_REVIEW


def test_accepts_explicit_accepted_status() -> None:
    relationship = _make(status=SemanticRelationshipStatus.ACCEPTED, evidence="same_chunk")

    assert relationship.status == SemanticRelationshipStatus.ACCEPTED
    assert relationship.evidence == "same_chunk"


def test_relationship_type_values_match_requested_taxonomy() -> None:
    expected = {
        "task_has_interval",
        "task_uses_procedure",
        "task_requires_spare_part",
        "task_requires_safety_warning",
        "equipment_has_procedure",
        "equipment_has_spare_part",
        "equipment_has_specification",
        "equipment_has_troubleshooting_entry",
        "manufacturer_has_contact_point",
        "supplier_has_contact_point",
    }

    actual = {member.value for member in SemanticRelationshipType}

    assert actual == expected

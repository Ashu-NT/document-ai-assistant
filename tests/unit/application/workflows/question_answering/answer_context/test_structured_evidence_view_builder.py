from src.application.workflows.question_answering.answer_context.structured_evidence_view_builder import (
    StructuredEvidenceViewBuilder,
)


def test_build_converts_entity_dict_into_typed_entity() -> None:
    builder = StructuredEvidenceViewBuilder()

    entities = builder.build(
        [
            {
                "manufacturer_id": "manufacturer_001",
                "name": "ACME Corp",
                "website": "https://acme.example",
                "source_chunk_id": "chunk_a",
                "_entity_type": "manufacturer",
            }
        ]
    )

    assert len(entities) == 1
    entity = entities[0]
    assert entity.entity_type == "manufacturer"
    assert entity.entity_id == "manufacturer_001"
    assert entity.source_chunk_id == "chunk_a"
    assert entity.fields["name"] == "ACME Corp"
    assert entity.fields["website"] == "https://acme.example"
    assert "_entity_type" not in entity.fields
    assert "related_entities" not in entity.fields
    assert entity.relationships == []


def test_build_skips_entries_without_an_entity_type() -> None:
    builder = StructuredEvidenceViewBuilder()

    entities = builder.build([{"name": "no type here"}, "not a dict"])

    assert entities == []


def test_build_falls_back_to_source_chunk_id_when_no_id_field_matches() -> None:
    builder = StructuredEvidenceViewBuilder()

    entities = builder.build(
        [
            {
                "name": "ACME Corp",
                "source_chunk_id": "chunk_manufacturer",
                "_entity_type": "manufacturer",
            }
        ]
    )

    assert entities[0].entity_id == "chunk_manufacturer"


def test_build_preserves_related_procedure_steps_through_relationship() -> None:
    """Regression test for 4.16: a maintenance task linked to a procedure
    via task_uses_procedure used to have the procedure's `steps` silently
    dropped one hop after StructuredEntityResolver resolved it (no
    "procedure" entry in StructuredFactKeyValueBuilder._ENTITY_FIELD_LABELS,
    and AnswerKeyValue.value can't hold a list anyway). The relationship's
    full target_entity_fields dict -- including `steps` -- must now survive
    into AnswerStructuredEntity.relationships instead of being flattened."""
    builder = StructuredEvidenceViewBuilder()

    entities = builder.build(
        [
            {
                "task_id": "task_001",
                "title": "Replace hydraulic filter",
                "interval": "Every 500 hours",
                "source_chunk_id": "chunk_task",
                "_entity_type": "maintenance_task",
                "related_entities": [
                    {
                        "relationship_type": "task_uses_procedure",
                        "direction": "outgoing",
                        "status": "accepted",
                        "confidence_score": 0.9,
                        "entity_type": "procedure",
                        "entity_id": "procedure_001",
                        "entity": {
                            "procedure_id": "procedure_001",
                            "title": "Replace hydraulic filter",
                            "steps": [
                                "Depressurize the line.",
                                "Remove the old filter.",
                                "Install the new filter.",
                            ],
                            "source_chunk_id": "chunk_procedure",
                        },
                    }
                ],
            }
        ]
    )

    assert len(entities) == 1
    task_entity = entities[0]
    assert task_entity.entity_type == "maintenance_task"
    assert len(task_entity.relationships) == 1
    relationship = task_entity.relationships[0]
    assert relationship.relationship_type == "task_uses_procedure"
    assert relationship.target_entity_type == "procedure"
    assert relationship.target_entity_id == "procedure_001"
    assert relationship.confidence_score == 0.9
    assert relationship.target_entity_fields["steps"] == [
        "Depressurize the line.",
        "Remove the old filter.",
        "Install the new filter.",
    ]


def test_build_ignores_malformed_related_entities() -> None:
    builder = StructuredEvidenceViewBuilder()

    entities = builder.build(
        [
            {
                "task_id": "task_001",
                "_entity_type": "maintenance_task",
                "related_entities": ["not a dict", {"entity_type": "procedure"}],
            }
        ]
    )

    assert len(entities[0].relationships) == 1
    assert entities[0].relationships[0].target_entity_type == "procedure"
    assert entities[0].relationships[0].target_entity_fields == {}

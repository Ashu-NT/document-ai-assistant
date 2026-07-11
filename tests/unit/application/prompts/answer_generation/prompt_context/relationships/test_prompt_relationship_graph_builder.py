from src.application.prompts.answer_generation.prompt_context.models import (
    PromptEntityView,
    PromptRelationshipView,
)
from src.application.prompts.answer_generation.prompt_context.relationships import (
    PromptRelationshipGraphBuilder,
)


def test_graph_builder_emits_edges_and_evidence_families() -> None:
    entities = [
        PromptEntityView(
            entity_type="maintenance_task",
            entity_id="task_001",
            source_chunk_id="chunk_001",
            fields={"title": "Replace hydraulic filter"},
            relationships=[
                PromptRelationshipView(
                    relationship_type="task_uses_procedure",
                    direction="outgoing",
                    status="accepted",
                    target_entity_type="procedure",
                    target_entity_id="procedure_001",
                    confidence_score=0.95,
                    target_entity_fields={"steps": ["Depressurize the line."]},
                )
            ],
        )
    ]

    edges, families = PromptRelationshipGraphBuilder().build(
        entities,
        source_number_by_chunk_id={"chunk_001": 7},
    )

    assert len(edges) == 1
    assert edges[0].source_entity_id == "task_001"
    assert edges[0].source_number == 7
    assert edges[0].relationship_type == "task_uses_procedure"
    assert edges[0].target_entity_id == "procedure_001"
    assert len(families) == 1
    assert families[0].anchor_entity_id == "task_001"
    assert families[0].anchor_source_number == 7
    assert families[0].edge_ids == ["edge_1"]
    assert families[0].relationship_types == ["task_uses_procedure"]
    assert families[0].related_entity_ids == ["procedure_001"]


def test_graph_builder_deduplicates_family_lists_but_keeps_all_edges() -> None:
    entities = [
        PromptEntityView(
            entity_type="manufacturer",
            entity_id="manufacturer_001",
            source_chunk_id="chunk_001",
            fields={"name": "ACME"},
            relationships=[
                PromptRelationshipView(
                    relationship_type="manufacturer_has_contact",
                    direction="outgoing",
                    status="accepted",
                    target_entity_type="contact_point",
                    target_entity_id="contact_001",
                    target_entity_fields={"value": "info@example.com"},
                ),
                PromptRelationshipView(
                    relationship_type="manufacturer_has_contact",
                    direction="outgoing",
                    status="accepted",
                    target_entity_type="contact_point",
                    target_entity_id="contact_001",
                    target_entity_fields={"value": "+49 123"},
                ),
            ],
        )
    ]

    edges, families = PromptRelationshipGraphBuilder().build(
        entities,
        source_number_by_chunk_id={"chunk_001": 3},
    )

    assert len(edges) == 2
    assert families[0].edge_ids == ["edge_1", "edge_2"]
    assert families[0].relationship_types == ["manufacturer_has_contact"]
    assert families[0].related_entity_ids == ["contact_001"]

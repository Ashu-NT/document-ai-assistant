from src.application.prompts.answer_generation.prompt_context.projectors import (
    PromptContextProjector,
)
from src.application.services.answer_generation import AnswerIntent
from src.application.workflows.question_answering.answer_context import (
    AnswerContextOrganizer,
    AnswerRelationship,
    AnswerStructuredEntity,
)
from src.domain.common import ChunkType
from src.domain.common.source_location import SourceLocation
from src.domain.retrieval.retrieved_chunk import RetrievedChunk


def _make_chunk(
    chunk_id: str = "chunk_001",
    content: str = "Replace hydraulic filter every 1000 hours.",
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        content=content,
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.MAINTENANCE_INTERVAL,
        section_path=["Maintenance", "Schedule"],
        source=SourceLocation(page_start=5, page_end=5),
    )


def test_projector_maps_structured_answer_context_into_prompt_bundle() -> None:
    context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.MAINTENANCE_SUMMARY,
        chunks=[_make_chunk()],
    )
    context.structured_entities.append(
        AnswerStructuredEntity(
            entity_type="maintenance_task",
            entity_id="task_001",
            fields={"title": "Replace hydraulic filter"},
            relationships=[
                AnswerRelationship(
                    relationship_type="task_uses_procedure",
                    direction="outgoing",
                    status="accepted",
                    target_entity_type="procedure",
                    target_entity_id="procedure_001",
                    target_entity_fields={"steps": ["Depressurize the line."]},
                )
            ],
        )
    )

    bundle = PromptContextProjector().project(context)

    assert bundle is not None
    assert bundle.answer_intent_value == "maintenance_summary"
    assert bundle.source_count == 1
    assert bundle.sources[0].document_title == "Current document"
    assert bundle.sources[0].section_path == "Maintenance > Schedule"
    assert bundle.entities[0].entity_type == "maintenance_task"
    assert bundle.entities[0].relationships[0].target_entity_id == "procedure_001"
    assert bundle.relationship_edges[0].source_entity_id == "task_001"
    assert bundle.relationship_edges[0].target_entity_id == "procedure_001"
    assert bundle.relationship_families[0].anchor_entity_id == "task_001"
    assert bundle.relationship_families[0].related_entity_ids == ["procedure_001"]
    assert bundle.maintenance_entries

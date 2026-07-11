from src.application.prompts.answer_generation.prompt_context.projectors import (
    PromptContextProjector,
)
from src.application.prompts.answer_generation.prompt_context.serializers import (
    StructuredEvidencePayloadSerializer,
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


def _make_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="chunk_001",
        document_id="doc_001",
        content="Test pressure: 700 bar",
        score=0.9,
        retrieval_source="dense",
        chunk_type=ChunkType.TECHNICAL_SPECIFICATION,
        section_path=["Specs"],
        source=SourceLocation(page_start=5, page_end=5),
        metadata={"table_rows_json": '[["Parameter","Value"],["Test pressure","700 bar"]]'},
    )


def test_serializer_preserves_nested_entity_relationships_and_first_class_tables() -> None:
    context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.TABLE_SUMMARY,
        chunks=[_make_chunk()],
    )
    context.structured_entities.append(
        AnswerStructuredEntity(
            entity_type="equipment",
            entity_id="equipment_001",
            fields={"name": "Hydraulic pump"},
            relationships=[
                AnswerRelationship(
                    relationship_type="equipment_has_specification",
                    direction="outgoing",
                    status="accepted",
                    target_entity_type="specification",
                    target_entity_id="spec_001",
                    target_entity_fields={
                        "parameter": "Test pressure",
                        "value": "700 bar",
                    },
                )
            ],
        )
    )

    bundle = PromptContextProjector().project(context)
    payload = StructuredEvidencePayloadSerializer().serialize(bundle)

    assert '"structured_entities"' in payload
    assert '"relationships"' not in payload
    assert '"relationship_edges"' in payload
    assert '"relationship_families"' in payload
    assert '"source_families"' in payload
    assert '"section_topology"' in payload
    assert '"source_groups"' not in payload
    assert '"section_groups"' not in payload
    assert '"relationship_type": "equipment_has_specification"' in payload
    assert '"source_entity_id": "equipment_001"' in payload
    assert '"target_entity_id": "spec_001"' in payload
    assert '"tables": [' in payload
    assert '"table_rows": [' not in payload
    assert '"headers": [' in payload
    assert '"cells_by_header": {' in payload
    assert '"Parameter"' in payload

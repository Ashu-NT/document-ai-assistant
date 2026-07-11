import json
from datetime import datetime

from src.application.prompts.answer_generation.prompt_context.models import (
    PromptContextBundle,
    PromptSourceView,
)
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
from src.application.workflows.question_answering.answer_context.models import (
    AnswerKeyValue,
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


def test_serializer_does_not_crash_on_non_json_native_entity_field_values() -> None:
    """Regression test: a resolved entity's raw fields can carry values
    straight from ORM-derived data (e.g. a `datetime` audit timestamp)
    that were never meant to survive into a JSON-serialization boundary.
    json.dumps must not crash on these -- it should stringify them, the
    same `default=str` fallback already used elsewhere in this codebase
    for arbitrary domain payloads (ocr_trace.py, quality_report_writer.py,
    plan_validator.py)."""
    context = AnswerContextOrganizer().organize(
        answer_intent=AnswerIntent.GENERAL,
        chunks=[_make_chunk()],
    )
    installed_at = datetime(2024, 1, 1, 12, 30)
    context.structured_entities.append(
        AnswerStructuredEntity(
            entity_type="equipment",
            entity_id="equipment_001",
            fields={"name": "Hydraulic pump", "installed_at": installed_at},
        )
    )

    bundle = PromptContextProjector().project(context)
    payload = StructuredEvidencePayloadSerializer().serialize(bundle)

    assert str(installed_at) in payload


def test_serializer_caps_arrays_larger_than_the_max_item_limit() -> None:
    key_values = [
        AnswerKeyValue(key=f"Key {i}", value=f"Value {i}", unit=None, source_number=1)
        for i in range(25)
    ]
    bundle = PromptContextBundle(
        answer_intent_value=AnswerIntent.GENERAL.value,
        source_count=1,
        sources=[
            PromptSourceView(source_number=1, chunk_id="chunk_001", content="")
        ],
        key_values=key_values,
    )

    payload = json.loads(StructuredEvidencePayloadSerializer().serialize(bundle))

    assert len(payload["key_values"]) == 20
    assert payload["key_values"][0]["key"] == "Key 0"
    assert payload["key_values"][-1]["key"] == "Key 19"


def test_serializer_does_not_truncate_arrays_under_the_cap() -> None:
    key_values = [
        AnswerKeyValue(key=f"Key {i}", value=f"Value {i}", unit=None, source_number=1)
        for i in range(3)
    ]
    bundle = PromptContextBundle(
        answer_intent_value=AnswerIntent.GENERAL.value,
        source_count=1,
        sources=[
            PromptSourceView(source_number=1, chunk_id="chunk_001", content="")
        ],
        key_values=key_values,
    )

    payload = json.loads(StructuredEvidencePayloadSerializer().serialize(bundle))

    assert len(payload["key_values"]) == 3
    assert [item["key"] for item in payload["key_values"]] == [
        "Key 0",
        "Key 1",
        "Key 2",
    ]


def test_serializer_emits_compact_json_with_no_indentation() -> None:
    bundle = PromptContextProjector().project(
        AnswerContextOrganizer().organize(
            answer_intent=AnswerIntent.GENERAL,
            chunks=[_make_chunk()],
        )
    )

    payload = StructuredEvidencePayloadSerializer().serialize(bundle)

    assert "\n" not in payload
    assert json.loads(payload) is not None

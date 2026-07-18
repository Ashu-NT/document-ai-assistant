from src.application.workflows.linking.chunk_cross_reference_relationship_candidate_builder import (
    EVIDENCE_EXPLICIT_CHUNK_CROSS_REFERENCE,
    ChunkCrossReferenceRelationshipCandidateBuilder,
)
from src.application.workflows.linking.semantic_entity_index import (
    IndexedEntity,
    SemanticEntityIndex,
)
from src.domain.document.entities import (
    ChunkCrossReference,
    ChunkCrossReferenceResolutionStatus,
    ChunkCrossReferenceType,
)
from src.domain.extraction import SemanticEntityType, SemanticRelationshipType


def _entity(entity_type, entity_id, *, chunk_id) -> IndexedEntity:
    return IndexedEntity(
        entity_type=entity_type,
        entity_id=entity_id,
        chunk_id=chunk_id,
        section_id=None,
        parent_section_id=None,
        table_id=None,
        page_start=None,
        nearby_chunk_ids=(),
    )


def _cross_reference(
    *,
    source_chunk_id: str,
    target_chunk_id: str | None,
) -> ChunkCrossReference:
    return ChunkCrossReference(
        cross_reference_id="xref_1",
        document_id="doc_001",
        source_chunk_id=source_chunk_id,
        reference_type=ChunkCrossReferenceType.PAGE_REFERENCE,
        matched_text="(→ Page 42)",
        target_page=42,
        target_chunk_id=target_chunk_id,
        resolution_status=(
            ChunkCrossReferenceResolutionStatus.RESOLVED_UNIQUE
            if target_chunk_id
            else ChunkCrossReferenceResolutionStatus.UNRESOLVED
        ),
        confidence_score=0.9 if target_chunk_id else 0.0,
    )


def _builder() -> ChunkCrossReferenceRelationshipCandidateBuilder:
    return ChunkCrossReferenceRelationshipCandidateBuilder()


def test_produces_a_high_confidence_candidate_for_a_matching_entity_pair() -> None:
    task = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_1", chunk_id="chunk_source")
    procedure = _entity(
        SemanticEntityType.PROCEDURE, "procedure_1", chunk_id="chunk_target"
    )
    index = SemanticEntityIndex([task, procedure])
    cross_reference = _cross_reference(
        source_chunk_id="chunk_source", target_chunk_id="chunk_target"
    )

    candidates = _builder().build(cross_references=[cross_reference], index=index)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.relationship_type == SemanticRelationshipType.TASK_USES_PROCEDURE
    assert candidate.source_entity_id == "task_1"
    assert candidate.target_entity_id == "procedure_1"
    assert candidate.evidence == EVIDENCE_EXPLICIT_CHUNK_CROSS_REFERENCE
    assert candidate.score == 0.95


def test_score_is_higher_than_the_highest_proximity_evidence_tier() -> None:
    # Confidence ordering matters: an authored reference should always beat
    # inferred proximity, but never outrank a real resolved FK (1.0).
    from src.application.workflows.linking.semantic_relationship_candidate_generator import (
        EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY,
        _SCORE_BY_EVIDENCE,
    )

    highest_proximity_score = _SCORE_BY_EVIDENCE[EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY]
    task = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_1", chunk_id="chunk_source")
    procedure = _entity(
        SemanticEntityType.PROCEDURE, "procedure_1", chunk_id="chunk_target"
    )
    index = SemanticEntityIndex([task, procedure])
    cross_reference = _cross_reference(
        source_chunk_id="chunk_source", target_chunk_id="chunk_target"
    )

    candidate = _builder().build(cross_references=[cross_reference], index=index)[0]

    assert candidate.score > highest_proximity_score
    assert candidate.score < 1.0


def test_ignores_an_unresolved_cross_reference() -> None:
    task = _entity(SemanticEntityType.MAINTENANCE_TASK, "task_1", chunk_id="chunk_source")
    index = SemanticEntityIndex([task])
    cross_reference = _cross_reference(source_chunk_id="chunk_source", target_chunk_id=None)

    candidates = _builder().build(cross_references=[cross_reference], index=index)

    assert candidates == []


def test_produces_no_candidate_when_neither_chunk_has_an_indexed_entity() -> None:
    index = SemanticEntityIndex([])
    cross_reference = _cross_reference(
        source_chunk_id="chunk_source", target_chunk_id="chunk_target"
    )

    candidates = _builder().build(cross_references=[cross_reference], index=index)

    assert candidates == []


def test_produces_no_candidate_when_entity_types_do_not_form_a_known_pair() -> None:
    manufacturer = _entity(
        SemanticEntityType.MANUFACTURER, "manufacturer_1", chunk_id="chunk_source"
    )
    supplier = _entity(SemanticEntityType.SUPPLIER, "supplier_1", chunk_id="chunk_target")
    index = SemanticEntityIndex([manufacturer, supplier])
    cross_reference = _cross_reference(
        source_chunk_id="chunk_source", target_chunk_id="chunk_target"
    )

    candidates = _builder().build(cross_references=[cross_reference], index=index)

    assert candidates == []

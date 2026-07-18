from __future__ import annotations

from src.application.workflows.linking.semantic_entity_index import IndexedEntity
from src.domain.extraction import SemanticEntityType, SemanticRelationshipType

# The 5 relationship types with no existing foreign-key mechanism, shared by
# every candidate-generation source that pairs up two already-extracted
# entities (proximity windowing, and the explicit chunk-cross-reference
# source) -- moved out of `semantic_relationship_candidate_generator.py` so
# it's importable without coupling to that class's window-walking logic.
# Order is (source_type, target_type, relationship_type); direction is fixed
# by this definition, not by which side a match is found on.
CANDIDATE_TYPE_PAIRS: tuple[
    tuple[SemanticEntityType, SemanticEntityType, SemanticRelationshipType], ...
] = (
    (
        SemanticEntityType.MAINTENANCE_TASK,
        SemanticEntityType.PROCEDURE,
        SemanticRelationshipType.TASK_USES_PROCEDURE,
    ),
    (
        SemanticEntityType.MAINTENANCE_TASK,
        SemanticEntityType.SPARE_PART,
        SemanticRelationshipType.TASK_REQUIRES_SPARE_PART,
    ),
    (
        SemanticEntityType.MAINTENANCE_TASK,
        SemanticEntityType.SAFETY_WARNING,
        SemanticRelationshipType.TASK_REQUIRES_SAFETY_WARNING,
    ),
    (
        SemanticEntityType.EQUIPMENT,
        SemanticEntityType.SPARE_PART,
        SemanticRelationshipType.EQUIPMENT_HAS_SPARE_PART,
    ),
    (
        SemanticEntityType.EQUIPMENT,
        SemanticEntityType.SPECIFICATION,
        SemanticRelationshipType.EQUIPMENT_HAS_SPECIFICATION,
    ),
)


def match_entity_pair(
    a: IndexedEntity, b: IndexedEntity
) -> tuple[IndexedEntity, IndexedEntity, SemanticRelationshipType] | None:
    """Checks whether two entities' types form one of the known candidate
    pairs, returning them ordered (source, target) per that pair's fixed
    direction, or None if they don't match any pair."""
    for source_type, target_type, relationship_type in CANDIDATE_TYPE_PAIRS:
        if a.entity_type == source_type and b.entity_type == target_type:
            return a, b, relationship_type
        if b.entity_type == source_type and a.entity_type == target_type:
            return b, a, relationship_type
    return None


__all__ = ["CANDIDATE_TYPE_PAIRS", "match_entity_pair"]

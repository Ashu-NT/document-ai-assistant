import itertools
from dataclasses import dataclass

from src.application.workflows.linking.semantic_entity_index import (
    IndexedEntity,
    SemanticEntityIndex,
)
from src.application.workflows.linking.semantic_relationship_type_pairs import (
    match_entity_pair,
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

# A page-adjacency window of 1 means entities on the same page or on
# immediately adjacent pages are eligible for a "nearby_page" candidate.
_NEARBY_PAGE_WINDOW = 1

EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY = "same_table_and_chunk_proximity"
EVIDENCE_SAME_CHUNK = "same_chunk"
EVIDENCE_SAME_SECTION = "same_section"
EVIDENCE_NEARBY_CHUNK = "nearby_chunk"
EVIDENCE_SAME_PARENT_SECTION = "same_parent_section"
EVIDENCE_NEARBY_PAGE = "nearby_page"
EVIDENCE_EXISTING_FK = "existing_fk"

_SCORE_BY_EVIDENCE = {
    EVIDENCE_EXISTING_FK: 1.0,
    EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY: 0.85,
    EVIDENCE_SAME_CHUNK: 0.8,
    EVIDENCE_SAME_SECTION: 0.65,
    EVIDENCE_NEARBY_CHUNK: 0.5,
    EVIDENCE_SAME_PARENT_SECTION: 0.35,
    EVIDENCE_NEARBY_PAGE: 0.3,
}


@dataclass(slots=True, frozen=True)
class RelationshipCandidate:
    relationship_type: SemanticRelationshipType
    source_entity_type: SemanticEntityType
    source_entity_id: str
    target_entity_type: SemanticEntityType
    target_entity_id: str
    evidence: str
    score: float


class SemanticRelationshipCandidateGenerator:
    """Generates relationship candidates for the 5 proximity-discovered
    relationship types by walking a `SemanticEntityIndex`'s window buckets,
    never comparing every entity pair in the document.

    "Same table" alone never fires a candidate: `table_row_id` is not
    populated (no row-level table parsing exists), so two different rows in
    a large table would otherwise incorrectly bucket together. Requiring
    chunk proximity alongside shared `table_id` uses chunk-adjacency as a
    practical proxy for "same row".
    """

    def generate(self, index: SemanticEntityIndex) -> list[RelationshipCandidate]:
        best: dict[tuple[str, str], RelationshipCandidate] = {}

        def consider(a: IndexedEntity, b: IndexedEntity, evidence: str) -> None:
            match = match_entity_pair(a, b)
            if match is None:
                return
            source, target, relationship_type = match

            candidate = RelationshipCandidate(
                relationship_type=relationship_type,
                source_entity_type=source.entity_type,
                source_entity_id=source.entity_id,
                target_entity_type=target.entity_type,
                target_entity_id=target.entity_id,
                evidence=evidence,
                score=_SCORE_BY_EVIDENCE[evidence],
            )

            key = (source.entity_id, target.entity_id)
            existing = best.get(key)
            if existing is None or candidate.score > existing.score:
                best[key] = candidate

        for table_entities in index.by_table.values():
            for a, b in itertools.combinations(table_entities, 2):
                if a.chunk_id and (
                    a.chunk_id == b.chunk_id or b.chunk_id in a.nearby_chunk_ids
                ):
                    consider(a, b, EVIDENCE_SAME_TABLE_AND_CHUNK_PROXIMITY)

        for chunk_entities in index.by_chunk.values():
            for a, b in itertools.combinations(chunk_entities, 2):
                consider(a, b, EVIDENCE_SAME_CHUNK)

        for section_entities in index.by_section.values():
            for a, b in itertools.combinations(section_entities, 2):
                consider(a, b, EVIDENCE_SAME_SECTION)

        for entity in index.entities:
            for nearby_chunk_id in entity.nearby_chunk_ids:
                for other in index.by_chunk.get(nearby_chunk_id, ()):
                    if other.entity_id == entity.entity_id:
                        continue
                    consider(entity, other, EVIDENCE_NEARBY_CHUNK)

        for parent_entities in index.by_parent_section.values():
            for a, b in itertools.combinations(parent_entities, 2):
                consider(a, b, EVIDENCE_SAME_PARENT_SECTION)

        # `index.sorted_by_page` only ever contains entities with a page_start
        # (filtered when the index was built), so these are never None here.
        sorted_entities = index.sorted_by_page
        for position, a in enumerate(sorted_entities):
            assert a.page_start is not None
            for b in sorted_entities[position + 1 :]:
                assert b.page_start is not None
                if b.page_start - a.page_start > _NEARBY_PAGE_WINDOW:
                    break
                consider(a, b, EVIDENCE_NEARBY_PAGE)

        return list(best.values())


def generate_fk_passthrough_candidates(
    *,
    maintenance_tasks: list[MaintenanceTask],
    maintenance_intervals: list[MaintenanceInterval],
    equipment: list[EquipmentInfo],
    procedures: list[Procedure],
    troubleshooting_entries: list[TroubleshootingEntry],
) -> list[RelationshipCandidate]:
    """Materialize the 3 relationship types that already exist as real,
    LLM-resolved foreign keys, bypassing windowing/scoring entirely.

    Only emits a relationship when the target FK actually resolves against
    the loaded entity set, so a stale/unresolved FK value does not produce
    a relationship pointing at nothing.
    """
    candidates: list[RelationshipCandidate] = []

    task_ids = {task.task_id for task in maintenance_tasks}
    equipment_ids = {item.equipment_id for item in equipment}

    for interval in maintenance_intervals:
        if interval.maintenance_task_id and interval.maintenance_task_id in task_ids:
            candidates.append(
                RelationshipCandidate(
                    relationship_type=SemanticRelationshipType.TASK_HAS_INTERVAL,
                    source_entity_type=SemanticEntityType.MAINTENANCE_TASK,
                    source_entity_id=interval.maintenance_task_id,
                    target_entity_type=SemanticEntityType.MAINTENANCE_INTERVAL,
                    target_entity_id=interval.maintenance_interval_id,
                    evidence=EVIDENCE_EXISTING_FK,
                    score=_SCORE_BY_EVIDENCE[EVIDENCE_EXISTING_FK],
                )
            )

    for procedure in procedures:
        if procedure.equipment_id and procedure.equipment_id in equipment_ids:
            candidates.append(
                RelationshipCandidate(
                    relationship_type=SemanticRelationshipType.EQUIPMENT_HAS_PROCEDURE,
                    source_entity_type=SemanticEntityType.EQUIPMENT,
                    source_entity_id=procedure.equipment_id,
                    target_entity_type=SemanticEntityType.PROCEDURE,
                    target_entity_id=procedure.procedure_id,
                    evidence=EVIDENCE_EXISTING_FK,
                    score=_SCORE_BY_EVIDENCE[EVIDENCE_EXISTING_FK],
                )
            )

    for entry in troubleshooting_entries:
        if entry.equipment_id and entry.equipment_id in equipment_ids:
            candidates.append(
                RelationshipCandidate(
                    relationship_type=(
                        SemanticRelationshipType.EQUIPMENT_HAS_TROUBLESHOOTING_ENTRY
                    ),
                    source_entity_type=SemanticEntityType.EQUIPMENT,
                    source_entity_id=entry.equipment_id,
                    target_entity_type=SemanticEntityType.TROUBLESHOOTING_ENTRY,
                    target_entity_id=entry.troubleshooting_id,
                    evidence=EVIDENCE_EXISTING_FK,
                    score=_SCORE_BY_EVIDENCE[EVIDENCE_EXISTING_FK],
                )
            )

    return candidates

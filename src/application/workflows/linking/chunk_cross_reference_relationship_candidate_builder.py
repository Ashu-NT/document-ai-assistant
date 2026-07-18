from __future__ import annotations

import itertools

from src.application.workflows.linking.semantic_entity_index import SemanticEntityIndex
from src.application.workflows.linking.semantic_relationship_candidate_generator import (
    RelationshipCandidate,
)
from src.application.workflows.linking.semantic_relationship_type_pairs import (
    match_entity_pair,
)
from src.domain.document.entities import ChunkCrossReference

# Higher than every proximity-discovered evidence tier in
# `semantic_relationship_candidate_generator.py` (max 0.85, same-table +
# chunk proximity) but below EVIDENCE_EXISTING_FK (1.0, a real LLM-resolved
# foreign key): an explicit, authored cross-reference ("(-> Page 1062)") is
# stronger evidence than any inferred proximity, since a human/manufacturer
# deliberately pointed from one passage to another, but it is still a
# heuristic resolution (page/section lookup, occasionally ambiguous), not a
# verified identity match the way a resolved FK is.
EVIDENCE_EXPLICIT_CHUNK_CROSS_REFERENCE = "explicit_chunk_cross_reference"
_SCORE_EXPLICIT_CHUNK_CROSS_REFERENCE = 0.95


class ChunkCrossReferenceRelationshipCandidateBuilder:
    """Builds entity-to-entity relationship candidates from resolved
    `ChunkCrossReference` rows (same-document inline references like "(->
    Page 1062)", detected/resolved by `ChunkCrossReferenceLinker` at
    ingestion time), by checking whether any already-extracted entities sit
    on either end of the reference.

    This is the "fusion" between the chunk-level cross-reference system and
    the entity-level semantic-linking system: neither replaces the other --
    a maintenance task's explicit page reference to a procedure produces a
    real `TASK_USES_PROCEDURE` relationship here with much higher confidence
    than the existing proximity-window discovery could ever assign it,
    since proximity is capped at a 1-page window and can never reach an
    intentionally-authored, arbitrarily-distant reference.
    """

    def build(
        self,
        *,
        cross_references: list[ChunkCrossReference],
        index: SemanticEntityIndex,
    ) -> list[RelationshipCandidate]:
        best: dict[tuple[str, str], RelationshipCandidate] = {}

        for cross_reference in cross_references:
            if cross_reference.target_chunk_id is None:
                continue

            source_entities = index.by_chunk.get(cross_reference.source_chunk_id, [])
            target_entities = index.by_chunk.get(cross_reference.target_chunk_id, [])
            if not source_entities or not target_entities:
                continue

            for source_entity, target_entity in itertools.product(
                source_entities, target_entities
            ):
                if source_entity.entity_id == target_entity.entity_id:
                    continue

                match = match_entity_pair(source_entity, target_entity)
                if match is None:
                    continue
                source, target, relationship_type = match

                candidate = RelationshipCandidate(
                    relationship_type=relationship_type,
                    source_entity_type=source.entity_type,
                    source_entity_id=source.entity_id,
                    target_entity_type=target.entity_type,
                    target_entity_id=target.entity_id,
                    evidence=EVIDENCE_EXPLICIT_CHUNK_CROSS_REFERENCE,
                    score=_SCORE_EXPLICIT_CHUNK_CROSS_REFERENCE,
                )

                key = (source.entity_id, target.entity_id)
                existing = best.get(key)
                if existing is None or candidate.score > existing.score:
                    best[key] = candidate

        return list(best.values())


__all__ = [
    "ChunkCrossReferenceRelationshipCandidateBuilder",
    "EVIDENCE_EXPLICIT_CHUNK_CROSS_REFERENCE",
]

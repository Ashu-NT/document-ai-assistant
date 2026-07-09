from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class AnswerRelationship:
    """Preserves a resolved structured-entity relationship (e.g. a
    maintenance task's linked procedure) as a typed view instead of
    flattening it into a single AnswerKeyValue string, which cannot hold
    the related entity's own fields -- see plan sections 4.2, 4.16, 9.3."""

    relationship_type: str
    direction: str
    status: str
    target_entity_type: str
    target_entity_id: str
    confidence_score: float | None = None
    target_entity_fields: dict[str, object] = field(default_factory=dict)

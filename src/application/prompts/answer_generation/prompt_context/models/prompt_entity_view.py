from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptRelationshipView:
    relationship_type: str
    direction: str
    status: str
    target_entity_type: str
    target_entity_id: str
    confidence_score: float | None = None
    target_entity_fields: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PromptEntityView:
    entity_type: str
    entity_id: str
    fields: dict[str, object] = field(default_factory=dict)
    source_chunk_id: str | None = None
    relationships: list[PromptRelationshipView] = field(default_factory=list)

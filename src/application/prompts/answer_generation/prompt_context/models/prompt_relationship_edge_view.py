from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptRelationshipEdgeView:
    edge_id: str
    source_entity_type: str
    source_entity_id: str
    source_chunk_id: str | None = None
    source_number: int | None = None
    relationship_type: str = ""
    direction: str = ""
    status: str = ""
    confidence_score: float | None = None
    target_entity_type: str = ""
    target_entity_id: str = ""
    target_entity_fields: dict[str, object] = field(default_factory=dict)

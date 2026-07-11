from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PromptEvidenceFamilyView:
    family_id: str
    anchor_entity_type: str
    anchor_entity_id: str
    anchor_source_number: int | None = None
    edge_ids: list[str] = field(default_factory=list)
    relationship_types: list[str] = field(default_factory=list)
    related_entity_ids: list[str] = field(default_factory=list)
    related_entity_types: list[str] = field(default_factory=list)

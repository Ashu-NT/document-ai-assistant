from __future__ import annotations

from dataclasses import dataclass, field

from src.application.workflows.retrieval.structured.structured_entity_type import (
    StructuredEntityType,
)
from src.domain.common import IdentifierType


@dataclass(slots=True)
class StructuredEvidenceQueryAnalysis:
    entity_types: list[StructuredEntityType] = field(default_factory=list)
    identifier_types: list[IdentifierType] = field(default_factory=list)
    detail_entity_type: StructuredEntityType | None = None
    wants_identifier_inventory: bool = False

    def has_entity_types(self) -> bool:
        return bool(self.entity_types)

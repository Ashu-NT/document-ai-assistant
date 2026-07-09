from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.document.entities.identifier import Identifier
from src.domain.retrieval import RetrievedChunk


@dataclass(slots=True)
class StructuredEvidenceBundle:
    identifiers: list[Identifier] = field(default_factory=list)
    structured_entities: list[dict[str, Any]] = field(default_factory=list)
    chunks: list[RetrievedChunk] = field(default_factory=list)
    diagnostics: dict[str, object] = field(default_factory=dict)

    def has_results(self) -> bool:
        return bool(self.identifiers or self.structured_entities or self.chunks)

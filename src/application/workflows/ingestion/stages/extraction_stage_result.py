from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExtractionStageResult:
    extraction_result: object | None
    deterministic_identifier_count: int
    semantic_relationship_count: int | None

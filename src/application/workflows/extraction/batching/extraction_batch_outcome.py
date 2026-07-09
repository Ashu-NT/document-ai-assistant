from dataclasses import dataclass, field

from src.domain.extraction import ExtractionResult


@dataclass(slots=True)
class ExtractionBatchOutcome:
    partial_results: list[ExtractionResult] = field(default_factory=list)
    attempted_chunk_ids: list[str] = field(default_factory=list)
    unresolved_chunk_ids: list[str] = field(default_factory=list)

    def extend(self, other: "ExtractionBatchOutcome") -> None:
        self.partial_results.extend(other.partial_results)
        self.attempted_chunk_ids.extend(other.attempted_chunk_ids)
        self.unresolved_chunk_ids.extend(other.unresolved_chunk_ids)

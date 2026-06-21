from dataclasses import dataclass, field

from src.domain.retrieval import RetrievedChunk


@dataclass(slots=True, frozen=True)
class DuplicateGroup:
    representative: RetrievedChunk
    collapsed_chunks: list[RetrievedChunk] = field(default_factory=list)
    reason: str | None = None
    representative_selection_reason: str | None = None

    @property
    def group_size(self) -> int:
        return 1 + len(self.collapsed_chunks)


from dataclasses import dataclass, field

from src.application.workflows.retrieval.deduplication.duplicate_group import (
    DuplicateGroup,
)
from src.domain.retrieval import RetrievedChunk


@dataclass(slots=True, frozen=True)
class RetrievalDeduplicationResult:
    chunks: list[RetrievedChunk]
    groups: list[DuplicateGroup] = field(default_factory=list)


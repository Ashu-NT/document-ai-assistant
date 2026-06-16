from dataclasses import dataclass, field

from src.domain.common import AuditMetadata


@dataclass(slots=True)
class MemoryEntry:
    memory_id: str

    content: str
    memory_type: str

    source_id: str | None = None
    source_type: str | None = None

    importance_score: float | None = None
    is_active: bool = True

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def is_important(self, threshold: float = 0.7) -> bool:
        if self.importance_score is None:
            return False
        return self.importance_score >= threshold
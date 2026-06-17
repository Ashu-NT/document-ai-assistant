from src.domain.memory import MemoryEntry
from src.infrastructure.db.orm_models import MemoryEntryORM


class MemoryEntryMapper:
    @staticmethod
    def to_orm(entry: MemoryEntry) -> MemoryEntryORM:
        return MemoryEntryORM(
            id=entry.memory_id,
            content=entry.content,
            memory_type=entry.memory_type,
            source_id=entry.source_id,
            source_type=entry.source_type,
            importance_score=entry.importance_score,
            is_active=entry.is_active,
            created_at=entry.audit.created_at,
        )

    @staticmethod
    def to_domain(orm: MemoryEntryORM) -> MemoryEntry:
        return MemoryEntry(
            memory_id=orm.id,
            content=orm.content,
            memory_type=orm.memory_type,
            source_id=orm.source_id,
            source_type=orm.source_type,
            importance_score=orm.importance_score,
            is_active=orm.is_active,
        )
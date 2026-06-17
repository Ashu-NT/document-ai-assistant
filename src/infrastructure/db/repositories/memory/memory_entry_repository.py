from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.memory import MemoryEntry
from src.infrastructure.db.mappers import MemoryEntryMapper
from src.infrastructure.db.orm_models import MemoryEntryORM
from src.shared.exceptions import DatabaseError


class MemoryEntryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, memory_entry: MemoryEntry) -> None:
        try:
            self.session.merge(MemoryEntryMapper.to_orm(memory_entry))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save memory entry.",
                details={"memory_id": memory_entry.memory_id},
            ) from exc

    def search(self, query: str, limit: int) -> list[MemoryEntry]:
        try:
            statement = (
                select(MemoryEntryORM)
                .where(MemoryEntryORM.content.ilike(f"%{query}%"))
                .where(MemoryEntryORM.is_active.is_(True))
                .limit(limit)
            )

            rows = self.session.execute(statement).scalars().all()

            return [MemoryEntryMapper.to_domain(row) for row in rows]

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to search memory entries.",
                details={"query": query, "limit": limit},
            ) from exc
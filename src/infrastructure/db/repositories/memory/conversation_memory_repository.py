from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.domain.memory import ConversationMemory
from src.infrastructure.db.mappers import ConversationMemoryMapper
from src.infrastructure.db.orm_models import ConversationMemoryORM, ConversationMessageORM
from src.shared.exceptions import DatabaseError


class ConversationMemoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, memory: ConversationMemory) -> None:
        try:
            self.session.merge(ConversationMemoryMapper.memory_to_orm(memory))

            for message in memory.messages:
                self.session.merge(
                    ConversationMemoryMapper.message_to_orm(
                        message,
                        conversation_id=memory.conversation_id,
                    )
                )

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to save conversation memory.",
                details={"conversation_id": memory.conversation_id},
            ) from exc

    def get(self, conversation_id: str) -> ConversationMemory | None:
        try:
            memory_row = self.session.get(ConversationMemoryORM, conversation_id)

            if memory_row is None:
                return None

            message_rows = self.session.execute(
                select(ConversationMessageORM)
                .where(ConversationMessageORM.conversation_id == conversation_id)
                .order_by(ConversationMessageORM.created_at)
            ).scalars().all()

            return ConversationMemoryMapper.to_domain(memory_row, message_rows)

        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Failed to load conversation memory.",
                details={"conversation_id": conversation_id},
            ) from exc
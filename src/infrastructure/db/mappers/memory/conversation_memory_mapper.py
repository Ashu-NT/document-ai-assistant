from src.domain.memory import ConversationMemory, ConversationMessage
from src.infrastructure.db.orm_models import ConversationMemoryORM, ConversationMessageORM


class ConversationMemoryMapper:
    @staticmethod
    def memory_to_orm(memory: ConversationMemory) -> ConversationMemoryORM:
        return ConversationMemoryORM(
            id=memory.conversation_id,
            created_at=memory.audit.created_at,
        )

    @staticmethod
    def message_to_orm(
        message: ConversationMessage,
        conversation_id: str,
    ) -> ConversationMessageORM:
        return ConversationMessageORM(
            id=message.message_id,
            conversation_id=conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.audit.created_at,
        )

    @staticmethod
    def to_domain(
        memory_row: ConversationMemoryORM,
        message_rows: list[ConversationMessageORM],
    ) -> ConversationMemory:
        memory = ConversationMemory(conversation_id=memory_row.id)

        for row in message_rows:
            memory.add_message(
                ConversationMessage(
                    message_id=row.id,
                    role=row.role,
                    content=row.content,
                )
            )

        return memory
from sqlalchemy.orm import Session

from src.application.contracts.memory import MemoryRepository
from src.domain.memory import ConversationMemory, MemoryEntry, SemanticMemoryReference
from src.infrastructure.db.repositories.memory.conversation_memory_repository import (
    ConversationMemoryRepository,
)
from src.infrastructure.db.repositories.memory.memory_entry_repository import (
    MemoryEntryRepository,
)
from src.infrastructure.db.repositories.memory.semantic_memory_repository import (
    SemanticMemoryRepository,
)


class SqlAlchemyMemoryRepository(MemoryRepository):
    def __init__(self, session: Session) -> None:
        self.conversations = ConversationMemoryRepository(session)
        self.entries = MemoryEntryRepository(session)
        self.semantic_references = SemanticMemoryRepository(session)

    def save_conversation_memory(self, memory: ConversationMemory) -> None:
        self.conversations.save(memory)

    def get_conversation_memory(
        self,
        conversation_id: str,
    ) -> ConversationMemory | None:
        return self.conversations.get(conversation_id)

    def save_memory_entry(self, memory_entry: MemoryEntry) -> None:
        self.entries.save(memory_entry)

    def search_memory_entries(
        self,
        query: str,
        limit: int,
    ) -> list[MemoryEntry]:
        return self.entries.search(query, limit)

    def save_semantic_reference(
        self,
        reference: SemanticMemoryReference,
    ) -> None:
        self.semantic_references.save(reference)
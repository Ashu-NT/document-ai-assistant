from typing import Protocol

from src.domain.memory import ConversationMemory, MemoryEntry, SemanticMemoryReference


class MemoryRepository(Protocol):
    def save_conversation_memory(self, memory: ConversationMemory) -> None:
        ...

    def get_conversation_memory(
        self,
        conversation_id: str,
    ) -> ConversationMemory | None:
        ...

    def save_memory_entry(self, memory_entry: MemoryEntry) -> None:
        ...

    def search_memory_entries(
        self,
        query: str,
        limit: int,
    ) -> list[MemoryEntry]:
        ...

    def save_semantic_reference(
        self,
        reference: SemanticMemoryReference,
    ) -> None:
        ...
from dataclasses import dataclass, field

from src.domain.memory.conversation_memory import ConversationMessage
from src.domain.memory.memory_entry import MemoryEntry
from src.domain.memory.semantic_memory import SemanticMemoryReference


@dataclass(slots=True)
class MemoryContext:
    conversation_id: str | None = None

    recent_messages: list[ConversationMessage] = field(default_factory=list)
    relevant_memories: list[MemoryEntry] = field(default_factory=list)
    semantic_references: list[SemanticMemoryReference] = field(default_factory=list)

    def has_context(self) -> bool:
        return bool(
            self.recent_messages
            or self.relevant_memories
            or self.semantic_references
        )
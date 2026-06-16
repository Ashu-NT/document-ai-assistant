from dataclasses import dataclass, field

from src.domain.common import AuditMetadata


@dataclass(slots=True)
class ConversationMessage:
    message_id: str
    role: str
    content: str

    audit: AuditMetadata = field(default_factory=AuditMetadata)


@dataclass(slots=True)
class ConversationMemory:
    conversation_id: str

    messages: list[ConversationMessage] = field(default_factory=list)

    audit: AuditMetadata = field(default_factory=AuditMetadata)

    def add_message(self, message: ConversationMessage) -> None:
        self.messages.append(message)

    def latest_messages(self, limit: int) -> list[ConversationMessage]:
        return self.messages[-limit:]

    def is_empty(self) -> bool:
        return not self.messages
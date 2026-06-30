from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.agent_runtime.session.conversation_turn import ConversationTurn


@dataclass(slots=True)
class ConversationHistory:
    turns: list[ConversationTurn] = field(default_factory=list)

    @classmethod
    def from_messages(cls, messages: list[dict[str, Any]] | None) -> "ConversationHistory":
        history = cls()
        for message in messages or []:
            if not isinstance(message, dict):
                continue
            turn = ConversationTurn.from_message(message)
            if turn is not None:
                history.turns.append(turn)
        return history

    def append(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)

    def extend_from_messages(self, messages: list[dict[str, Any]] | None) -> None:
        updated = self.from_messages(messages)
        self.turns = updated.turns

    def clear(self) -> None:
        self.turns.clear()

    def is_empty(self) -> bool:
        return not self.turns

    def recent(self, limit: int = 10) -> list[ConversationTurn]:
        if limit <= 0:
            return []
        return self.turns[-limit:]

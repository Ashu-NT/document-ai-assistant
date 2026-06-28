from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class ConversationMemory:
    def __init__(self, *, max_messages: int = 20) -> None:
        self.max_messages = max_messages
        self._messages: deque[dict[str, Any]] = deque(maxlen=max_messages)

    def append_user_message(
        self,
        content: str,
        *,
        conversation_id: str | None = None,
    ) -> None:
        self._append("user", content, conversation_id=conversation_id)

    def append_assistant_message(
        self,
        content: str,
        *,
        conversation_id: str | None = None,
    ) -> None:
        self._append("assistant", content, conversation_id=conversation_id)

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def _append(
        self,
        role: str,
        content: str,
        *,
        conversation_id: str | None,
    ) -> None:
        self._messages.append(
            {
                "role": role,
                "content": content,
                "conversation_id": conversation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

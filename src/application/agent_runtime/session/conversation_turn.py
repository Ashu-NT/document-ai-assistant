from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class ConversationTurn:
    role: str
    content: str
    timestamp: str

    @classmethod
    def from_message(cls, message: dict[str, Any]) -> "ConversationTurn" | None:
        role = str(message.get("role") or "").strip()
        content = str(message.get("content") or "").strip()
        if not role or not content:
            return None
        timestamp = str(message.get("timestamp") or _utc_now_iso())
        return cls(
            role=role,
            content=content,
            timestamp=timestamp,
        )

    @classmethod
    def create(cls, *, role: str, content: str) -> "ConversationTurn":
        return cls(
            role=role,
            content=content,
            timestamp=_utc_now_iso(),
        )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

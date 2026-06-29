from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any

from src.application.langgraph.memory.session_state_store import SessionStateStore


class ConversationMemory:
    def __init__(
        self,
        *,
        max_messages: int = 20,
        session_state_store: SessionStateStore | None = None,
    ) -> None:
        self.max_messages = max_messages
        self.session_state_store = session_state_store
        self._messages: deque[dict[str, Any]] = deque(maxlen=max_messages)
        self._loaded_session_id: str | None = None
        self._selected_document_id: str | None = None
        self._selected_document_title: str | None = None
        self._selected_document_file_name: str | None = None
        self._pending_clarification: dict[str, Any] | None = None
        self._clarification_options: list[dict[str, Any]] = []
        self._clarification_question: str | None = None

    def append_user_message(
        self,
        content: str,
        *,
        conversation_id: str | None = None,
    ) -> None:
        self._ensure_session_loaded(conversation_id)
        self._append("user", content, conversation_id=conversation_id)
        self._persist(conversation_id)

    def append_assistant_message(
        self,
        content: str,
        *,
        conversation_id: str | None = None,
    ) -> None:
        self._ensure_session_loaded(conversation_id)
        self._append("assistant", content, conversation_id=conversation_id)
        self._persist(conversation_id)

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._messages)

    def load_session(self, session_id: str | None) -> dict[str, Any]:
        self._loaded_session_id = session_id
        snapshot: dict[str, Any] | None = None
        if session_id and self.session_state_store is not None:
            snapshot = self.session_state_store.get(session_id)
        self._apply_snapshot(snapshot or {})
        return self.snapshot()

    def save_session_state(
        self,
        *,
        session_id: str | None,
        selected_document_id: str | None,
        selected_document_title: str | None,
        selected_document_file_name: str | None,
        pending_clarification: dict[str, Any] | None,
        clarification_options: list[dict[str, Any]] | None,
        clarification_question: str | None,
    ) -> None:
        self._ensure_session_loaded(session_id)
        self._selected_document_id = selected_document_id
        self._selected_document_title = selected_document_title
        self._selected_document_file_name = selected_document_file_name
        self._pending_clarification = pending_clarification
        self._clarification_options = list(clarification_options or [])
        self._clarification_question = clarification_question
        self._persist(session_id)

    def snapshot(self) -> dict[str, Any]:
        return {
            "history": list(self._messages),
            "selected_document_id": self._selected_document_id,
            "selected_document_title": self._selected_document_title,
            "selected_document_file_name": self._selected_document_file_name,
            "pending_clarification": self._pending_clarification,
            "clarification_options": list(self._clarification_options),
            "clarification_question": self._clarification_question,
        }

    def clear(self, session_id: str | None = None) -> None:
        resolved_session_id = session_id or self._loaded_session_id
        self._messages.clear()
        self._selected_document_id = None
        self._selected_document_title = None
        self._selected_document_file_name = None
        self._pending_clarification = None
        self._clarification_options = []
        self._clarification_question = None
        if resolved_session_id and self.session_state_store is not None:
            self.session_state_store.clear(resolved_session_id)
        if session_id is not None:
            self._loaded_session_id = session_id
        elif resolved_session_id is None:
            self._loaded_session_id = None

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

    def _ensure_session_loaded(self, session_id: str | None) -> None:
        resolved_session_id = session_id or self._loaded_session_id
        if resolved_session_id == self._loaded_session_id:
            return
        self.load_session(resolved_session_id)

    def _apply_snapshot(self, snapshot: dict[str, Any]) -> None:
        history = snapshot.get("history", [])
        self._messages = deque(
            (entry for entry in history if isinstance(entry, dict)),
            maxlen=self.max_messages,
        )
        self._selected_document_id = _coerce_optional_str(snapshot.get("selected_document_id"))
        self._selected_document_title = _coerce_optional_str(
            snapshot.get("selected_document_title")
        )
        self._selected_document_file_name = _coerce_optional_str(
            snapshot.get("selected_document_file_name")
        )
        pending_clarification = snapshot.get("pending_clarification")
        self._pending_clarification = (
            dict(pending_clarification)
            if isinstance(pending_clarification, dict)
            else None
        )
        clarification_options = snapshot.get("clarification_options", [])
        self._clarification_options = [
            dict(option)
            for option in clarification_options
            if isinstance(option, dict)
        ]
        self._clarification_question = _coerce_optional_str(
            snapshot.get("clarification_question")
        )

    def _persist(self, session_id: str | None) -> None:
        resolved_session_id = session_id or self._loaded_session_id
        if not resolved_session_id or self.session_state_store is None:
            return
        self.session_state_store.save(resolved_session_id, self.snapshot())


def _coerce_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)

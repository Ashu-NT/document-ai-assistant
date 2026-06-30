from __future__ import annotations

from typing import Any

from src.application.agent_runtime.session.conversation_history import ConversationHistory
from src.application.agent_runtime.session.conversation_turn import ConversationTurn
from src.application.agent_runtime.session.selected_document_state import (
    SelectedDocumentState,
)
from src.application.agent_runtime.session.session import RuntimeOptions, Session


class SessionManager:
    def create_session(
        self,
        *,
        session_id: str,
        runtime_options: RuntimeOptions,
        snapshot: dict[str, Any] | None = None,
    ) -> Session:
        session = Session(
            session_id=session_id,
            runtime_options=runtime_options,
        )
        if snapshot:
            self.apply_snapshot(session, snapshot)
        return session

    def apply_snapshot(
        self,
        session: Session,
        snapshot: dict[str, Any],
    ) -> None:
        session.selected_document = SelectedDocumentState(
            document_id=_optional_str(snapshot.get("selected_document_id")),
            title=_optional_str(snapshot.get("selected_document_title")),
            file_name=_optional_str(snapshot.get("selected_document_file_name")),
        )
        session.pending_clarification = _coerce_optional_dict(
            snapshot.get("pending_clarification")
        )
        session.conversation_history = ConversationHistory.from_messages(
            snapshot.get("history")
            if isinstance(snapshot.get("history"), list)
            else []
        )
        session.touch()

    def update_from_graph_result(
        self,
        session: Session,
        *,
        result: Any,
        react_trace: Any | None = None,
    ) -> None:
        data = getattr(result, "data", {}) or {}
        session.selected_document = SelectedDocumentState.from_graph_data(data)
        session.pending_clarification = _coerce_optional_dict(
            data.get("pending_clarification")
        )
        session.last_route = _optional_str(getattr(result, "route", None))
        session.last_trace = react_trace
        session.last_research_plan = _coerce_optional_dict(data.get("research_plan"))
        session.last_retrieval_strategy = _coerce_optional_dict(
            data.get("retrieval_strategy_decision")
        )
        session.last_context_chunks = _coerce_dict_list(data.get("context_chunks"))
        session.last_citations = _coerce_dict_list(data.get("citations"))
        session.last_result = result
        messages = getattr(result, "messages", None)
        if isinstance(messages, list):
            session.conversation_history = ConversationHistory.from_messages(messages)
        session.touch()

    def record_local_exchange(
        self,
        session: Session,
        *,
        user_input: str,
        response_text: str,
    ) -> None:
        session.conversation_history.append(
            ConversationTurn.create(role="user", content=user_input)
        )
        session.conversation_history.append(
            ConversationTurn.create(role="assistant", content=response_text)
        )
        session.touch()

    def clear_document(self, session: Session) -> None:
        session.clear_document()

    def reset(self, session: Session) -> None:
        session.reset_runtime_state()


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _coerce_optional_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return dict(value)
    return None


def _coerce_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]

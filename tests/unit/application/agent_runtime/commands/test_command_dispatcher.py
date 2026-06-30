from src.application.agent_runtime.commands import CommandDispatcher
from src.application.agent_runtime.session import RuntimeOptions, Session, SessionManager
from src.application.langgraph.common import GraphResult


class _GuardedAgent:
    def __init__(self) -> None:
        self.calls = []

    def __getattr__(self, name: str):
        if "llm" in name or "qdrant" in name:
            raise AssertionError(f"Unexpected direct access to {name}")
        raise AttributeError(name)

    def execute_graph_command(self, user_input: str, *, session: Session):
        self.calls.append(user_input)
        if user_input.startswith("open "):
            return GraphResult.ok(
                response_text="Selected document: FWC12 Manual.",
                route="select_document",
                data={
                    "selected_document_id": "doc_001",
                    "selected_document_title": "FWC12 Manual",
                    "selected_document_file_name": "FWC12 Manual.pdf",
                },
                messages=[
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": "Selected document: FWC12 Manual."},
                ],
            )
        return GraphResult.ok(
            response_text="Cleared selected document.",
            route="clear_document",
            data={
                "selected_document_id": None,
                "selected_document_title": None,
                "selected_document_file_name": None,
            },
            messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": "Cleared selected document."},
            ],
        )

    def extract_list_documents(self, result):
        return []

    def extract_selected_document(self, result):
        return {"title": "FWC12 Manual"}

    def export_latest_trace(self, session):
        return None

    def build_status_payload(self, session):
        return {"session_id": session.session_id}

    def build_settings_payload(self, session):
        return {"quiet": session.runtime_options.quiet}

    def reset_session(self, session):
        session.reset_runtime_state()


def _build_session() -> Session:
    return SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )


def test_help_returns_grouped_help() -> None:
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("/help", agent=_GuardedAgent(), session=_build_session())

    assert result is not None
    assert result.success is True
    assert "Documents" in result.data["groups"]
    assert result.data["groups"]["Documents"][0]["command"] == "/list"
    assert "indexed documents" in result.data["groups"]["Documents"][0]["description"].lower()


def test_exit_sets_should_exit() -> None:
    dispatcher = CommandDispatcher()

    result = dispatcher.dispatch("/exit", agent=_GuardedAgent(), session=_build_session())

    assert result is not None
    assert result.should_exit is True


def test_current_shows_selected_document() -> None:
    dispatcher = CommandDispatcher()
    session = _build_session()
    session.selected_document.title = "FWC12 Manual"

    result = dispatcher.dispatch("/current", agent=_GuardedAgent(), session=session)

    assert result is not None
    assert result.render_as == "current_document"
    assert result.data["document_name"] == "FWC12 Manual"


def test_history_returns_conversation_turns() -> None:
    dispatcher = CommandDispatcher()
    session = _build_session()
    session.conversation_history.append(
        __import__("src.application.agent_runtime.session", fromlist=["ConversationTurn"]).ConversationTurn.create(
            role="user",
            content="What is the maintenance interval?",
        )
    )

    result = dispatcher.dispatch("/history", agent=_GuardedAgent(), session=session)

    assert result is not None
    assert result.render_as == "history"
    assert len(result.data["turns"]) == 1


def test_commands_do_not_call_llm_or_qdrant_directly() -> None:
    dispatcher = CommandDispatcher()
    agent = _GuardedAgent()

    result = dispatcher.dispatch("/open FWC12", agent=agent, session=_build_session())

    assert result is not None
    assert result.success is True
    assert agent.calls == ["open FWC12"]

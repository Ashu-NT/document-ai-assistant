from dataclasses import dataclass

from src.application.agent_runtime.commands import CommandDispatcher
from src.application.agent_runtime.demo_agent import DemoAgent
from src.application.agent_runtime.policies import DemoVisibilityPolicy
from src.application.agent_runtime.presenters import JsonPresenter, MarkdownPresenter
from src.application.agent_runtime.react_loop import ReactTraceBuilder
from src.application.agent_runtime.session import RuntimeOptions, SessionManager
from src.application.agent_runtime.tracing import DemoTraceWriter
from src.application.langgraph.common import GraphResult


@dataclass
class _RuntimeStatus:
    document_count: int = 3
    embedding_index_status: str = "Ready"
    model_name: str = "qwen3:8b"
    capabilities: list[str] = None

    def __post_init__(self) -> None:
        if self.capabilities is None:
            self.capabilities = ["Question Answering"]


class _FakeRuntime:
    def __init__(self) -> None:
        self.runtime_settings = {
            "generation_enabled": True,
            "general_llm": "qwen3:8b",
            "planning_llm": "qwen3:8b",
            "ollama_base_url": "http://localhost:11434",
        }
        self.runtime_status = _RuntimeStatus()

    def run_graph_request(self, user_input: str, **kwargs):
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
                trace=[{"node_name": "find_document", "elapsed_ms": 12.0, "tool_name": "find_document"}],
            )
        if user_input == "clear document":
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
                trace=[{"node_name": "session_command", "elapsed_ms": 5.0}],
            )
        return GraphResult.ok(
            response_text="Answer text.",
            route="answer_question",
            data={
                "answer": "Answer text.",
                "selected_document_id": "doc_001",
                "selected_document_title": "FWC12 Manual",
                "context_chunks": [],
                "citations": [],
            },
            messages=[
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": "Answer text."},
            ],
            trace=[{"node_name": "answer_question", "elapsed_ms": 25.0, "tool_name": "answer_question"}],
        )

    def clear_persisted_session(self, session_id: str | None) -> None:
        return None


def _build_demo_agent() -> DemoAgent:
    session_manager = SessionManager()
    session = session_manager.create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    return DemoAgent(
        runtime=_FakeRuntime(),
        session=session,
        session_manager=session_manager,
        command_dispatcher=CommandDispatcher(),
        trace_builder=ReactTraceBuilder(),
        visibility_policy=DemoVisibilityPolicy(),
        trace_writer=DemoTraceWriter(
            markdown_presenter=MarkdownPresenter(),
            json_presenter=JsonPresenter(),
            output_dir="outputs/demo_agent/test_demo_agent",
        ),
    )


def test_open_updates_selected_document() -> None:
    agent = _build_demo_agent()

    handled = agent.process_input("/open FWC12")

    assert handled.command_result is not None
    assert agent.session.selected_document.display_name == "FWC12 Manual"


def test_close_clears_selected_document() -> None:
    agent = _build_demo_agent()
    agent.process_input("/open FWC12")

    handled = agent.process_input("/close")

    assert handled.command_result is not None
    assert agent.session.selected_document.is_selected is False

from pathlib import Path

from src.application.agent_runtime.presenters import JsonPresenter, MarkdownPresenter
from src.application.agent_runtime.react_loop import ReactTrace, ReactStep
from src.application.agent_runtime.react_loop.react_event import ReactEvent
from src.application.agent_runtime.session import RuntimeOptions, SessionManager
from src.application.agent_runtime.tracing import DemoTraceWriter
from src.application.langgraph.common import GraphResult


def _build_trace_dependencies(tmp_path: Path):
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={"selected_document_title": "FWC12 Manual"},
    )
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text.", "context_chunks": [], "citations": []},
        messages=[
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Answer text."},
        ],
    )
    trace = ReactTrace(
        route="answer_question",
        steps=[
            ReactStep(
                index=1,
                event_type=ReactEvent.THOUGHT_SUMMARY,
                title="Thought Summary",
                body="Retrieve grounded evidence first.",
            )
        ],
    )
    writer = DemoTraceWriter(
        markdown_presenter=MarkdownPresenter(),
        json_presenter=JsonPresenter(),
        output_dir=tmp_path,
    )
    return session, result, trace, writer


def test_trace_writer_creates_unique_files(tmp_path: Path) -> None:
    session, result, trace, writer = _build_trace_dependencies(tmp_path)

    first = writer.write_latest_trace(session=session, result=result, react_trace=trace)
    second = writer.write_latest_trace(session=session, result=result, react_trace=trace)

    assert first["markdown_path"] != second["markdown_path"]
    assert Path(first["markdown_path"]).exists()
    assert Path(second["json_path"]).exists()


def test_export_command_handles_no_trace() -> None:
    from src.application.agent_runtime.commands.builtins.export_command import ExportCommand
    from src.application.agent_runtime.commands.slash_command import SlashCommand

    class _Agent:
        def export_latest_trace(self, session):
            return None

    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = ExportCommand().execute(
        SlashCommand(name="export", raw_text="/export"),
        agent=_Agent(),
        session=session,
    )

    assert result.success is False
    assert result.message == "No trace is available to export yet."


def test_export_command_exports_latest_trace(tmp_path: Path) -> None:
    from src.application.agent_runtime.commands.builtins.export_command import ExportCommand
    from src.application.agent_runtime.commands.slash_command import SlashCommand

    class _Agent:
        def __init__(self) -> None:
            self.session, self.result, self.trace, self.writer = _build_trace_dependencies(tmp_path)

        def export_latest_trace(self, session):
            return self.writer.write_latest_trace(
                session=self.session,
                result=self.result,
                react_trace=self.trace,
            )

    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = ExportCommand().execute(
        SlashCommand(name="export", raw_text="/export"),
        agent=_Agent(),
        session=session,
    )

    assert result.success is True
    assert "markdown_path" in result.data

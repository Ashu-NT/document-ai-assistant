from src.application.agent_runtime.commands import CommandResult

from src.application.agent_runtime.policies import DemoVisibilityPolicy

from src.application.agent_runtime.presenters import ConsolePresenter

from src.application.agent_runtime.react_loop import ReactTrace, ReactStep

from src.application.agent_runtime.react_loop.react_event import ReactEvent

from src.application.agent_runtime.session import RuntimeOptions, SessionManager

from src.application.langgraph.common import GraphResult

def _build_session():
    return SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={"selected_document_title": "FWC12 Manual"},
    )

def test_presenter_output_unchanged_when_new_fields_absent() -> None:
    """Backward-compatibility regression check: an answer that doesn't use
    sections/reference_notes/limitation_note (today's normal case) must
    render with no trace of the new blocks/footer field."""
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text.", "citations": [{"chunk_id": "chunk_1"}]},
    )

    output = presenter.render_graph_result(
        user_input="Question",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "Sections" not in output
    assert "Reference Notes" not in output
    assert "Limitation" not in output

def test_presenter_does_not_duplicate_banner_per_turn() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text."},
    )

    output = presenter.render_graph_result(
        user_input="Question",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "Document AI Agent" not in output

def test_presenter_renders_professional_help_with_descriptions() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    command_result = CommandResult(
        success=True,
        message="Help",
        data={
            "groups": {
                "Documents": [
                    {
                        "command": "/list",
                        "description": "List indexed documents available in the corpus.",
                    },
                    {
                        "command": "/open <document>",
                        "description": "Select a document for follow-up questions and research.",
                    },
                ]
            },
            "examples": [],
        },
        render_as="help",
    )

    output = presenter.render_command_result(
        command_result,
        session=session,
        policy=DemoVisibilityPolicy(),
    )

    assert "Documents" in output
    assert "/list" in output
    assert "-- List indexed documents available in the corpus." in output
    assert "/open <document>" in output

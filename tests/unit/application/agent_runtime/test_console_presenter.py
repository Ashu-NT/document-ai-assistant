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


def test_presenter_renders_user_request_and_final_answer() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "citations": [{"chunk_id": "chunk_1"}],
        },
        trace=[{"elapsed_ms": 120.0}],
    )

    output = presenter.render_graph_result(
        user_input="What are the maintenance intervals?",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "User Request" in output
    assert "Final Answer" in output
    assert "Answer text." in output


def test_presenter_hides_internal_ids_by_default() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "selected_document_id": "doc_secret",
            "tool_results": {"raw": {"id": "chunk_secret"}},
        },
    )

    output = presenter.render_graph_result(
        user_input="Question",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "doc_secret" not in output
    assert "chunk_secret" not in output


def test_presenter_hides_raw_json_by_default() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    command_result = CommandResult(
        success=True,
        message="Runtime Settings",
        data={"raw_json": '{"secret": true}'},
        render_as="message",
    )

    output = presenter.render_command_result(
        command_result,
        session=session,
        policy=DemoVisibilityPolicy(),
    )

    assert output == "Runtime Settings"


def test_presenter_renders_status_footer_and_skips_missing_fields() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    trace = ReactTrace(
        route="answer_question",
        steps=[
            ReactStep(
                index=1,
                event_type=ReactEvent.THOUGHT_SUMMARY,
                title="Thought Summary",
                body="Retrieve evidence first.",
            )
        ],
    )
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "retrieval_strategy_decision": {"primary_strategy": "MAINTENANCE_LOOKUP"},
            "citations": [{"chunk_id": "chunk_1"}],
        },
        trace=[{"elapsed_ms": 2500.0}],
    )

    output = presenter.render_graph_result(
        user_input="Question",
        result=result,
        react_trace=trace,
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=True,
    )

    assert "Route      : answer_question" in output
    assert "Sources    : 1" in output
    assert "None" not in output


def test_presenter_shows_accept_with_limitations_footer_and_best_answer() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Daily, weekly, monthly, and annual maintenance intervals are listed on pp.58-59.",
        route="answer_question",
        data={
            "answer": "Daily, weekly, monthly, and annual maintenance intervals are listed on pp.58-59.",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "citations": [{"chunk_id": "chunk_58"}],
        },
    )

    output = presenter.render_graph_result(
        user_input="What are the maintenance intervals?",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "Daily, weekly, monthly, and annual maintenance intervals" in output
    assert "Reflection : ACCEPT_WITH_LIMITATIONS" in output


def test_presenter_shows_generated_answer_for_accept_when_response_text_is_safe_failure() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text=(
            "I could not verify a grounded answer confidently enough from the current "
            "document evidence."
        ),
        route="answer_question",
        data={
            "answer": "The part and serial number details are listed on p.50 and p.72.",
            "reflection_decision": "ACCEPT",
            "citations": [{"chunk_id": "chunk_50"}],
        },
    )

    output = presenter.render_graph_result(
        user_input="find part number or serial number",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "The part and serial number details are listed on p.50 and p.72." in output
    assert "I could not verify a grounded answer confidently enough" not in output
    assert "Reflection : ACCEPT" in output


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

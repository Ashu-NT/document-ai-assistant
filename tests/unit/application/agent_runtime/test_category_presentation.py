from src.application.agent_runtime.presenters import ConsolePresenter, JsonPresenter
from src.application.agent_runtime.policies import DemoVisibilityPolicy
from src.application.agent_runtime.react_loop import ReactTrace
from src.application.agent_runtime.session import RuntimeOptions, SessionManager
from src.application.langgraph.common import GraphResult


def _build_session():
    return SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={"selected_document_title": "FWC12 Manual"},
    )


def test_console_presenter_uses_safety_heading_for_safety_answers() -> None:
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="What are the safety warnings?",
        result=GraphResult.ok(
            response_text="Depressurize the line before opening the cover.",
            route="answer_question",
            data={
                "answer": "Depressurize the line before opening the cover.",
                "answer_intent": "safety_warnings",
            },
        ),
        react_trace=ReactTrace(route="answer_question"),
        session=_build_session(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "SAFETY WARNING" in output
    assert "Final Answer" not in output


def test_console_presenter_shows_render_provenance_for_structured_answers() -> None:
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="What are the maintenance intervals?",
        result=GraphResult.ok(
            response_text="table output",
            route="answer_question",
            data={
                "answer": "table output",
                "answer_intent": "maintenance_summary",
                "render_provenance": "parsed maintenance schedule data",
            },
        ),
        react_trace=ReactTrace(route="answer_question"),
        session=_build_session(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "Maintenance Schedule" in output
    assert "Answer From: parsed maintenance schedule data" in output


def test_json_presenter_includes_answer_intent_and_render_provenance() -> None:
    payload = JsonPresenter().render(
        session=_build_session(),
        result=GraphResult.ok(
            response_text="Answer text.",
            route="answer_question",
            data={
                "answer": "Answer text.",
                "answer_intent": "specification_summary",
                "render_provenance": "parsed structured fact data",
                "context_chunks": [],
                "citations": [],
            },
        ),
        react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )

    assert payload["answer_intent"] == "specification_summary"
    assert payload["render_provenance"] == "parsed structured fact data"

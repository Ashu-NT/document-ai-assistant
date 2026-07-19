"""Cross-format parity guard (Phase 4, finding F11/F12/F13/F14,
outputs/architecture/answering_and_prompt_fresh_audit.md): every
safety-relevant field the console shows for a turn must also reach JSON and
Markdown export -- so this class of gap (a field added to one output path
and forgotten in the others) fails a test instead of shipping silently."""

from src.application.agent_runtime.policies import DemoVisibilityPolicy
from src.application.agent_runtime.presenters import (
    ConsolePresenter,
    JsonPresenter,
    MarkdownPresenter,
)
from src.application.agent_runtime.react_loop import ReactTrace
from src.application.agent_runtime.session import RuntimeOptions, SessionManager
from src.application.langgraph.common import GraphResult


def _make_result() -> GraphResult:
    return GraphResult.ok(
        response_text="Replace the filter every 1000 hours.",
        route="answer_question",
        data={
            "answer": "Replace the filter every 1000 hours.",
            "limitation_note": "Only the primary interval was found.",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "reflection_result": {
                "decision": {
                    "decision": "ACCEPT_WITH_LIMITATIONS",
                    "reason": "Evidence only partially covers the interval.",
                }
            },
            "citations": [
                {
                    "document_name": "FWC12 Manual",
                    "section_title": "Maintenance > Filters",
                    "source": {"page_start": 12, "page_end": 12},
                }
            ],
            "post_answer_guardrail_warnings": [
                {
                    "decision": "WARN",
                    "reason": "Unresolved citation detected.",
                    "violations": ["Citation r2 has no matching source."],
                }
            ],
        },
        messages=[
            {"role": "user", "content": "When is the filter replaced?"},
            {"role": "assistant", "content": "Replace the filter every 1000 hours."},
        ],
    )


def _build_session():
    return SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={"selected_document_title": "FWC12 Manual"},
    )


def test_limitation_note_reaches_every_output_format() -> None:
    result = _make_result()
    session = _build_session()

    console = ConsolePresenter().render_graph_result(
        user_input="When is the filter replaced?",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    json_payload = JsonPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )
    markdown = MarkdownPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question")
    )

    assert "Only the primary interval was found." in console
    assert json_payload["limitation_note"] == "Only the primary interval was found."
    assert "Only the primary interval was found." in markdown


def test_guardrail_warnings_reach_every_output_format() -> None:
    result = _make_result()
    session = _build_session()

    console = ConsolePresenter().render_graph_result(
        user_input="When is the filter replaced?",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    json_payload = JsonPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )
    markdown = MarkdownPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question")
    )

    assert "Unresolved citation detected." in console
    assert json_payload["post_answer_guardrail_warnings"][0]["reason"] == (
        "Unresolved citation detected."
    )
    assert "Unresolved citation detected." in markdown


def test_reflection_status_reaches_every_output_format() -> None:
    result = _make_result()
    session = _build_session()

    console = ConsolePresenter().render_graph_result(
        user_input="When is the filter replaced?",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    json_payload = JsonPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )
    markdown = MarkdownPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question")
    )

    assert "ACCEPT_WITH_LIMITATIONS" in console
    assert json_payload["reflection"]["decision"] == "ACCEPT_WITH_LIMITATIONS"
    assert "ACCEPT_WITH_LIMITATIONS" in markdown


def test_citation_detail_reaches_every_output_format_not_just_a_count() -> None:
    result = _make_result()
    session = _build_session()

    console = ConsolePresenter().render_graph_result(
        user_input="When is the filter replaced?",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    json_payload = JsonPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )
    markdown = MarkdownPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question")
    )

    assert "FWC12 Manual, p.12 (Maintenance > Filters)" in console
    assert json_payload["citations"][0]["document_name"] == "FWC12 Manual"
    assert "FWC12 Manual, p.12 (Maintenance > Filters)" in markdown

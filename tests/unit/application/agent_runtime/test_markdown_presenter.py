from src.application.agent_runtime.presenters import MarkdownPresenter
from src.application.agent_runtime.react_loop import ReactTrace, ReactStep
from src.application.agent_runtime.react_loop.react_event import ReactEvent
from src.application.agent_runtime.session import RuntimeOptions, SessionManager
from src.application.langgraph.common import GraphResult


def test_markdown_has_expected_sections() -> None:
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={"selected_document_title": "FWC12 Manual"},
    )
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text.", "citations": [], "context_chunks": []},
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

    markdown = MarkdownPresenter().render(session=session, result=result, react_trace=trace)

    assert "# Document AI Demo Trace" in markdown
    assert "## Session" in markdown
    assert "## Agent Trace" in markdown
    assert "## Final Answer" in markdown


def test_markdown_excludes_raw_prompts() -> None:
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text.", "raw_llm_plan": '{"secret":"plan"}'},
        messages=[
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Answer text."},
        ],
    )

    markdown = MarkdownPresenter().render(
        session=session,
        result=result,
        react_trace=ReactTrace(route="answer_question"),
    )

    assert "secret" not in markdown

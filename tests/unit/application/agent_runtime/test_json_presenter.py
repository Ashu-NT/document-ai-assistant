from src.application.agent_runtime.presenters import JsonPresenter
from src.application.agent_runtime.react_loop import ReactTrace, ReactStep
from src.application.agent_runtime.react_loop.react_event import ReactEvent
from src.application.agent_runtime.session import RuntimeOptions, SessionManager
from src.application.langgraph.common import GraphResult


def test_json_has_expected_keys() -> None:
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
        snapshot={"selected_document_title": "FWC12 Manual"},
    )
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "selected_document_id": "doc_001",
            "context_chunks": [],
            "citations": [],
        },
        diagnostics={"safe": True},
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

    payload = JsonPresenter().render(
        session=session,
        result=result,
        react_trace=trace,
        include_trace=True,
    )

    assert payload["route"] == "answer_question"
    assert payload["success"] is True
    assert payload["answer"] == "Answer text."
    assert "trace" in payload


def test_json_excludes_raw_prompts_and_chain_of_thought() -> None:
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text.", "raw_llm_plan": '{"secret":"plan"}'},
    )

    payload = JsonPresenter().render(
        session=session,
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )

    assert "raw_llm_plan" not in payload
    assert "chain-of-thought" not in str(payload)

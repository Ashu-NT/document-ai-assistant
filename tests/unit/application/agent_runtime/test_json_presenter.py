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


def test_json_presenter_includes_sections_reference_notes_and_limitation_note() -> None:
    """finding 6.9: JSON export must carry the same structure the console
    shows -- sections, reference_notes, and limitation_note."""
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = GraphResult.ok(
        response_text="Replace the filter every 1000 hours.",
        route="answer_question",
        data={
            "answer": "Replace the filter every 1000 hours.",
            "sections": [
                {
                    "heading": "Interval",
                    "body": "Every 1000 hours.",
                    "reference_note_ids": ["r1"],
                }
            ],
            "reference_notes": [
                {
                    "note_id": "r1",
                    "claim_text": "Every 1000 operating hours.",
                    "source_number": 1,
                    "chunk_id": "chunk_1",
                }
            ],
            "limitation_note": "Only the primary interval was found.",
        },
    )

    payload = JsonPresenter().render(
        session=session,
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )

    assert payload["sections"] == [
        {
            "heading": "Interval",
            "body": "Every 1000 hours.",
            "reference_note_ids": ["r1"],
        }
    ]
    assert payload["reference_notes"][0]["note_id"] == "r1"
    assert payload["limitation_note"] == "Only the primary interval was found."


def test_json_presenter_uses_resolved_final_answer_for_accept_with_limitations() -> None:
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = GraphResult.ok(
        response_text=(
            "I could not verify a grounded answer confidently enough from the "
            "current document evidence."
        ),
        route="answer_question",
        data={
            "answer": "Weekly maintenance is required every 100 operating hours.",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": (
                            "Weekly maintenance is required every 100 operating hours."
                        )
                    },
                }
            },
        },
    )

    payload = JsonPresenter().render(
        session=session,
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        include_trace=False,
    )

    assert payload["answer"] == "Weekly maintenance is required every 100 operating hours."

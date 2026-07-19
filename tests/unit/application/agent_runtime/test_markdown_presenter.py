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


def test_markdown_includes_sections_reference_notes_and_limitation_note() -> None:
    """finding 6.9: Markdown export must carry the same structure the
    console shows -- sections, reference_notes, and limitation_note."""
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
                    "chunk_id": None,
                }
            ],
            "limitation_note": "Only the primary interval was found.",
        },
        messages=[
            {"role": "user", "content": "When is the filter replaced?"},
            {"role": "assistant", "content": "Replace the filter every 1000 hours."},
        ],
    )

    markdown = MarkdownPresenter().render(
        session=session,
        result=result,
        react_trace=ReactTrace(route="answer_question"),
    )

    assert "## Limitation" in markdown
    assert "Only the primary interval was found." in markdown
    assert "## Sections" in markdown
    assert "### Interval" in markdown
    assert "Every 1000 hours." in markdown
    assert "## Reference Notes" in markdown
    assert "[UNVERIFIED] [r1] Every 1000 operating hours. -> Source 1" in markdown


def test_markdown_renders_real_citation_detail_not_a_bare_count() -> None:
    """Finding F12: Markdown export used to reduce citations to a bare
    `- Citations: N` count, discarding exactly the checkable detail (page/
    section) the console shows."""
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = GraphResult.ok(
        response_text="Replace the filter every 1000 hours.",
        route="answer_question",
        data={
            "answer": "Replace the filter every 1000 hours.",
            "citations": [
                {
                    "document_name": "FWC12 Manual",
                    "section_title": "Maintenance > Filters",
                    "source": {"page_start": 12, "page_end": 12},
                }
            ],
        },
        messages=[
            {"role": "user", "content": "When is the filter replaced?"},
            {"role": "assistant", "content": "Replace the filter every 1000 hours."},
        ],
    )

    markdown = MarkdownPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question")
    )

    assert "## Citations" in markdown
    assert "FWC12 Manual, p.12 (Maintenance > Filters)" in markdown
    assert "Citations: 1" not in markdown


def test_markdown_includes_guardrail_notes_and_reflection_status() -> None:
    """Finding F13/F14: guardrail warnings and reflection status used to be
    visible only in the console, absent from Markdown export entirely."""
    session = SessionManager().create_session(
        session_id="demo-session",
        runtime_options=RuntimeOptions(),
    )
    result = GraphResult.ok(
        response_text="Replace the filter every 1000 hours.",
        route="answer_question",
        data={
            "answer": "Replace the filter every 1000 hours.",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "reflection_result": {
                "decision": {
                    "decision": "ACCEPT_WITH_LIMITATIONS",
                    "reason": "Evidence only partially covers the interval.",
                }
            },
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

    markdown = MarkdownPresenter().render(
        session=session, result=result, react_trace=ReactTrace(route="answer_question")
    )

    assert "## Reflection" in markdown
    assert "Decision: ACCEPT_WITH_LIMITATIONS" in markdown
    assert "Evidence only partially covers the interval." in markdown
    assert "## Guardrail Notes" in markdown
    assert "[WARN] Unresolved citation detected." in markdown
    assert "Citation r2 has no matching source." in markdown


def test_markdown_uses_resolved_final_answer_for_accept_with_limitations() -> None:
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

    markdown = MarkdownPresenter().render(
        session=session,
        result=result,
        react_trace=ReactTrace(route="answer_question"),
    )

    assert "Weekly maintenance is required every 100 operating hours." in markdown
    assert "I could not verify a grounded answer confidently enough" not in markdown

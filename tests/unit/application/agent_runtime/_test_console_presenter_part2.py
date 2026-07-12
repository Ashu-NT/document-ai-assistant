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


def test_presenter_renders_citations_with_page_labels() -> None:
    """finding 6.1: citations render with document/page/section a user can
    check, not just the bare `Sources: N` footer count."""
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "citations": [
                {
                    "citation_id": "cit_1",
                    "document_id": "doc_1",
                    "document_name": "FWC12 Manual",
                    "section_title": "Maintenance Schedule",
                    "source": {"page_start": 58, "page_end": 59},
                }
            ],
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

    assert "Citations" in output
    assert "- FWC12 Manual, pp.58-59 (Maintenance Schedule)" in output
    assert "Sources    : 1" in output


def test_presenter_renders_guardrail_warnings_when_present() -> None:
    """finding 5.1 follow-through: post_answer_guardrail_warnings is now
    reachable and must render somewhere -- purely additive."""
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "post_answer_guardrail_warnings": [
                {
                    "decision": "WARN",
                    "reason": "Citation could not be resolved to a known chunk.",
                    "violations": ["unresolved_citation:source_9"],
                }
            ],
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

    assert "Guardrail Notes" in output
    assert "[WARN] Citation could not be resolved to a known chunk." in output
    assert "unresolved_citation:source_9" in output


def test_presenter_omits_guardrail_notes_block_when_empty() -> None:
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text.", "post_answer_guardrail_warnings": []},
    )

    output = presenter.render_graph_result(
        user_input="Question",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "Guardrail Notes" not in output


def test_presenter_always_shows_reflection_reason_without_show_react() -> None:
    """finding 6.5: reflection's reason must appear by default, not only
    when the fuller --show-react trace is also requested."""
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "reflection_result": {
                "decision": {
                    "decision": "ACCEPT_WITH_LIMITATIONS",
                    "reason": "Evidence covered only one of two sub-questions.",
                },
            },
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

    assert (
        "Reflection : ACCEPT_WITH_LIMITATIONS - Evidence covered only one of "
        "two sub-questions." in output
    )


def test_presenter_shows_reflection_not_active_when_disabled() -> None:
    """Reflection-off visibility: diagnostics["reflection_enabled"] is the
    already-surfaced signal distinguishing "reflection never ran" from
    "reflection ran and accepted silently"."""
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={"answer": "Answer text."},
        diagnostics={"reflection_enabled": False},
    )

    output = presenter.render_graph_result(
        user_input="Question",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "Reflection : not active (self-check disabled)" in output


def test_presenter_omits_reflection_off_line_when_diagnostics_missing() -> None:
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

    assert "Reflection" not in output


def test_presenter_final_answer_keeps_guardrail_replacement() -> None:
    """finding 5.5 (this renderer's own independent copy): when
    response_text_guardrail_replaced is True, the safe-fallback text must
    win outright and must never be swapped back for the raw generated
    answer, even though the fallback text string-matches a safe-failure
    sentinel and reflection's decision is otherwise "usable"."""
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text=(
            "I could not verify a grounded answer confidently enough from the "
            "current document evidence."
        ),
        route="answer_question",
        data={
            "answer": "The secret internal part number is XZ-99-SECRET.",
            "reflection_decision": "ACCEPT",
            "response_text_guardrail_replaced": True,
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

    assert "I could not verify a grounded answer confidently enough" in output
    assert "XZ-99-SECRET" not in output


def test_presenter_sections_with_mixed_linked_and_orphaned_notes() -> None:
    """A note linked to a section renders grouped under it; a note not
    linked to any section still renders in the flat block -- covering
    finding 6.2's "avoid showing the same note twice" requirement without
    losing orphaned notes."""
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "sections": [
                {
                    "heading": "Interval",
                    "body": "Replace every 1000 hours.",
                    "reference_note_ids": ["r1"],
                }
            ],
            "reference_notes": [
                {
                    "note_id": "r1",
                    "claim_text": "Replace every 1000 operating hours.",
                    "source_number": 1,
                    "chunk_id": "chunk_001",
                },
                {
                    "note_id": "r2",
                    "claim_text": "An unrelated claim not tied to any section.",
                    "source_number": 2,
                    "chunk_id": "chunk_002",
                },
            ],
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

    assert "[r1] Replace every 1000 operating hours. -> Source 1" in output
    assert "Reference Notes" in output
    assert "[r2] An unrelated claim not tied to any section. -> Source 2" in output
    sections_index = output.index("Sections")
    r1_index = output.index("[r1]")
    reference_notes_heading_index = output.index("Reference Notes")
    r2_index = output.index("[r2]")
    assert sections_index < r1_index < reference_notes_heading_index < r2_index

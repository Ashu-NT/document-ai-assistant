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

def test_presenter_renders_sections_and_reference_notes() -> None:
    # finding 6.2: a reference note linked to a section (via
    # reference_note_ids) now renders grouped, indented, underneath that
    # section -- and is therefore no longer repeated in the separate flat
    # "Reference Notes" block, since that block only shows notes NOT linked
    # to any section (this test's single note IS linked, so that block must
    # not appear at all).
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="The filter is replaced every 1000 hours.",
        route="answer_question",
        data={
            "answer": "The filter is replaced every 1000 hours.",
            "sections": [
                {
                    "heading": "Maintenance interval",
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
                }
            ],
        },
    )

    output = presenter.render_graph_result(
        user_input="When should I replace the filter?",
        result=result,
        react_trace=ReactTrace(route="answer_question"),
        session=session,
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )

    assert "Sections" in output
    assert "Maintenance interval" in output
    assert "-" * len("Maintenance interval") in output
    assert "Replace every 1000 hours." in output
    assert "[r1] Replace every 1000 operating hours. -> Source 1" in output
    assert "(unverified)" not in output
    assert "[UNVERIFIED]" not in output
    assert "Reference Notes" not in output
    final_answer_index = output.index("Final Answer")
    sections_index = output.index("Sections")
    assert final_answer_index < sections_index

def test_presenter_flags_unresolved_reference_note() -> None:
    # finding 6.4: the unverified marker is now a leading, all-caps
    # [UNVERIFIED] tag rather than a low-visibility trailing "(unverified)"
    # suffix. This note has no section linking it, so it's "orphaned" and
    # still renders in the flat Reference Notes block (finding 6.2's
    # decision: that block shows notes not claimed by any section).
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "reference_notes": [
                {
                    "note_id": "r1",
                    "claim_text": "A claim that cites a source that doesn't exist.",
                    "source_number": 99,
                    "chunk_id": None,
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

    assert "Reference Notes" in output
    assert (
        "[UNVERIFIED] [r1] A claim that cites a source that doesn't exist. -> Source 99"
        in output
    )
    assert "(unverified)" not in output
    assert "chunk_001" not in output
    unverified_index = output.index("[UNVERIFIED]")
    note_id_index = output.index("[r1]")
    assert unverified_index < note_id_index

def test_presenter_renders_limitation_note_as_own_block() -> None:
    # finding 6.6: limitation_note gets its own labeled block right after
    # Final Answer instead of one more flat `label: value` row in the
    # footer alongside Elapsed -- it must no longer appear there.
    presenter = ConsolePresenter()
    session = _build_session()
    result = GraphResult.ok(
        response_text="Answer text.",
        route="answer_question",
        data={
            "answer": "Answer text.",
            "limitation_note": "Only the primary interval was found.",
            "citations": [{"chunk_id": "chunk_1"}],
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

    assert "Limitation" in output
    assert "Only the primary interval was found." in output
    assert "Limitation : Only the primary interval was found." not in output
    final_answer_index = output.index("Final Answer")
    limitation_index = output.index("Limitation")
    assert final_answer_index < limitation_index

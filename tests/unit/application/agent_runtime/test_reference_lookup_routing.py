from __future__ import annotations

from src.application.agent_runtime.react_loop.react_trace_builder import _thought_summary


def test_identifier_lookup_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "identifier_lookup"},
        "what are the manufacturer and supplier page references",
    )
    assert "identifier" in summary.lower()
    assert "exact values" in summary.lower()


def test_maintenance_summary_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "maintenance_summary"},
        "what are the maintenance intervals?",
    )
    assert "maintenance" in summary.lower()


def test_procedure_steps_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "procedure_steps"},
        "how do I replace the filter?",
    )
    assert "procedural" in summary.lower() or "steps" in summary.lower()


def test_safety_warnings_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "safety_warnings"},
        "what safety warnings apply?",
    )
    assert "safety" in summary.lower() or "caution" in summary.lower()


def test_troubleshooting_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "troubleshooting"},
        "the pump won't start — what do I check?",
    )
    assert "troubleshoot" in summary.lower() or "diagnostic" in summary.lower()


def test_specification_summary_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "specification_summary"},
        "what is the max operating pressure?",
    )
    assert "specification" in summary.lower()


def test_certification_summary_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "certification_summary"},
        "is this CE certified?",
    )
    assert "certification" in summary.lower() or "compliance" in summary.lower()


def test_table_summary_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "table_summary"},
        "show me the schedule table",
    )
    assert "table" in summary.lower() or "tabular" in summary.lower()


def test_document_summary_intent_produces_specific_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "document_summary"},
        "give me an overview of this document",
    )
    assert "overview" in summary.lower() or "summary" in summary.lower() or "section" in summary.lower()


def test_generic_answer_question_produces_grounded_summary():
    summary = _thought_summary(
        "answer_question",
        {"answer_intent": "general"},
        "what does this document say about calibration?",
    )
    assert "grounded" in summary.lower() or "evidence" in summary.lower()


def test_missing_intent_falls_back_to_generic():
    summary = _thought_summary(
        "answer_question",
        {},
        "some random question",
    )
    assert len(summary) > 0
    assert "grounded" in summary.lower() or "evidence" in summary.lower()


def test_deep_research_summary_mentions_synthesis():
    summary = _thought_summary(
        "deep_research",
        {},
        "compare troubleshooting and maintenance procedures",
    )
    assert "synthesis" in summary.lower() or "evidence" in summary.lower()


def test_planned_task_summary_mentions_plan():
    summary = _thought_summary(
        "planned_task",
        {},
        "do steps A then B then C",
    )
    assert "plan" in summary.lower()


def test_out_of_scope_summary_mentions_scope():
    summary = _thought_summary(
        "out_of_scope",
        {},
        "book me a flight",
    )
    assert "scope" in summary.lower()


def test_blocked_action_destructive():
    summary = _thought_summary(
        "blocked_action",
        {"unsafe_request_blocked": True},
        "delete all documents",
    )
    assert "destructive" in summary.lower() or "stop" in summary.lower()


def test_clarification_needed():
    summary = _thought_summary(
        "answer_question",
        {"pending_clarification": {"question": "Which document?"}},
        "tell me about it",
    )
    assert len(summary) > 0

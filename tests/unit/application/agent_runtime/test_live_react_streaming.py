from __future__ import annotations

import io

from src.application.agent_runtime.presenters.console_presenter import ConsolePresenter
from src.application.agent_runtime.react_loop.react_trace_builder import ReactTraceBuilder
from src.application.agent_runtime.policies.demo_visibility_policy import DemoVisibilityPolicy
from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)
from src.application.agent_runtime.streaming.live_event_sink import NullEventSink
from src.application.agent_runtime.streaming.console_event_sink import ConsoleLiveEventSink


class _FakeResult:
    def __init__(self, *, response_text=None, data=None, route="answer_question", success=True, trace=None):
        self.response_text = response_text
        self.data = data or {}
        self.route = route
        self.success = success
        self.trace = trace or []


class _FakeSession:
    class _Doc:
        display_name = "TestDoc"
    selected_document = _Doc()


# --- Reflection FAIL visibility tests ---

def test_reflection_fail_message_shown_not_stale_answer():
    result = _FakeResult(
        response_text="I could not verify a grounded answer confidently enough from the current evidence.",
        data={"answer": "The torque is 42 Nm."},  # stale LLM answer
    )
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="what is the torque?",
        result=result,
        react_trace=None,
        session=_FakeSession(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    assert "I could not verify" in output
    assert "The torque is 42 Nm" not in output


def test_reflection_pass_shows_answer():
    result = _FakeResult(
        response_text="The torque is 42 Nm.",
        data={"answer": "The torque is 42 Nm."},
    )
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="what is the torque?",
        result=result,
        react_trace=None,
        session=_FakeSession(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    assert "42 Nm" in output


def test_response_text_preferred_over_stale_data_answer():
    result = _FakeResult(
        response_text="Safe fallback message.",
        data={"answer": "Old generated answer."},
    )
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="query",
        result=result,
        react_trace=None,
        session=_FakeSession(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    assert "Safe fallback message." in output
    assert "Old generated answer." not in output


def test_when_response_text_absent_data_answer_shown():
    result = _FakeResult(
        response_text=None,
        data={"answer": "Answer from data."},
    )
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="query",
        result=result,
        react_trace=None,
        session=_FakeSession(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    assert "Answer from data." in output


def test_accept_with_limitations_shows_generated_answer_not_safe_failure():
    result = _FakeResult(
        response_text="I could not verify a grounded answer confidently enough from the current document evidence.",
        data={
            "answer": "Weekly maintenance latest after 100 operating hours (p.58).",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
        },
    )
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="what are the maintenance intervals?",
        result=result,
        react_trace=None,
        session=_FakeSession(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    assert "Weekly maintenance latest after 100 operating hours" in output
    assert "I could not verify a grounded answer confidently enough" not in output


def test_accept_shows_generated_answer_not_safe_failure():
    result = _FakeResult(
        response_text="I could not verify a grounded answer confidently enough from the current document evidence.",
        data={
            "answer": "The serial number is listed on p.50 and p.72.",
            "reflection_decision": "ACCEPT",
        },
    )
    presenter = ConsolePresenter()
    output = presenter.render_graph_result(
        user_input="find part number or serial number",
        result=result,
        react_trace=None,
        session=_FakeSession(),
        policy=DemoVisibilityPolicy(),
        show_react=False,
    )
    assert "The serial number is listed on p.50 and p.72." in output
    assert "I could not verify a grounded answer confidently enough" not in output


# --- NullEventSink tests ---

def test_null_sink_emits_nothing_to_stdout(capsys):
    sink = NullEventSink()
    for event_type in LiveAgentEventType:
        sink.emit(LiveAgentEvent(event_type=event_type, payload={}))
    captured = capsys.readouterr()
    assert captured.out == ""


# --- ConsoleLiveEventSink event ordering ---

def test_events_printed_in_emission_order():
    stream = io.StringIO()
    sink = ConsoleLiveEventSink(stream=stream)
    types = [
        LiveAgentEventType.RUN_STARTED,
        LiveAgentEventType.UNDERSTAND_REQUEST,
        LiveAgentEventType.ACTION_STARTED,
        LiveAgentEventType.ACTION_COMPLETED,
        LiveAgentEventType.FINAL_STARTED,
        LiveAgentEventType.RUN_COMPLETED,
    ]
    for et in types:
        sink.emit(LiveAgentEvent(event_type=et, payload={}))
    output = stream.getvalue()
    # Header appears once; Understand precedes Retrieve; silent events produce no output
    assert "Agent Loop" in output
    assert output.index("Understand") < output.index("Retrieve")


def test_deep_research_events_include_plan():
    stream = io.StringIO()
    sink = ConsoleLiveEventSink(stream=stream)
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.PLAN_COMPLETED,
        payload={"task_count": 4, "task_titles": ["Task A", "Task B", "Task C", "Task D"]},
    ))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.ACTION_STARTED))
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.ACTION_COMPLETED,
        payload={"description": "Retrieved 12 evidence chunk(s)."},
    ))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.RUN_COMPLETED))
    output = stream.getvalue()
    assert "Plan" in output
    assert "Task A" in output
    assert "Retrieved 12" in output

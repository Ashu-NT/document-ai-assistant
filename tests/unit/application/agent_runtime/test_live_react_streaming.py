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
    lines = [l for l in stream.getvalue().splitlines() if l.strip()]
    assert len(lines) == len(types)


def test_deep_research_events_include_plan():
    stream = io.StringIO()
    sink = ConsoleLiveEventSink(stream=stream)
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.PLAN_COMPLETED,
        payload={"task_count": 4},
    ))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.ACTION_STARTED))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.ACTION_COMPLETED, payload={"chunk_count": 12}))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.RUN_COMPLETED))
    output = stream.getvalue()
    assert "4 task(s)" in output
    assert "12 chunk(s)" in output

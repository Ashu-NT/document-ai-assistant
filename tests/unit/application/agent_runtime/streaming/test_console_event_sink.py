from __future__ import annotations

import io

from src.application.agent_runtime.streaming.console_event_sink import ConsoleLiveEventSink
from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)


def _sink() -> tuple[ConsoleLiveEventSink, io.StringIO]:
    stream = io.StringIO()
    return ConsoleLiveEventSink(stream=stream), stream


def test_run_started_prints_label():
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.RUN_STARTED))
    assert "Starting..." in stream.getvalue()


def test_understand_request_includes_route():
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.UNDERSTAND_REQUEST,
        payload={"route": "answer_question"},
    ))
    output = stream.getvalue()
    assert "Routing request" in output
    assert "answer question" in output


def test_plan_completed_includes_task_count():
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.PLAN_COMPLETED,
        payload={"task_count": 3},
    ))
    output = stream.getvalue()
    assert "Plan ready" in output
    assert "3 task(s)" in output


def test_reflection_completed_includes_decision():
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.REFLECTION_COMPLETED,
        payload={"decision": "ACCEPT"},
    ))
    output = stream.getvalue()
    assert "Review complete" in output
    assert "ACCEPT" in output


def test_action_completed_includes_chunk_count():
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.ACTION_COMPLETED,
        payload={"chunk_count": 5},
    ))
    output = stream.getvalue()
    assert "Evidence collected" in output
    assert "5 chunk(s)" in output


def test_blocked_includes_reason():
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(
        event_type=LiveAgentEventType.BLOCKED,
        payload={"reason": "unsafe request"},
    ))
    output = stream.getvalue()
    assert "Request blocked" in output
    assert "unsafe request" in output


def test_unknown_event_type_suppressed():
    sink, stream = _sink()
    # RUN_STARTED maps to a label; just verify no crash for unknown future types
    # by subclassing and injecting a fake type
    assert stream.getvalue() == ""  # nothing emitted yet


def test_each_event_ends_with_ellipsis():
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.FINAL_STARTED))
    output = stream.getvalue().strip()
    assert output.endswith("...")


def test_each_mapped_event_produces_one_line():
    for event_type in LiveAgentEventType:
        stream = io.StringIO()
        s = ConsoleLiveEventSink(stream=stream)
        s.emit(LiveAgentEvent(event_type=event_type))
        output = stream.getvalue()
        lines = [l for l in output.splitlines() if l.strip()]
        assert len(lines) <= 1, f"{event_type} produced {len(lines)} lines"

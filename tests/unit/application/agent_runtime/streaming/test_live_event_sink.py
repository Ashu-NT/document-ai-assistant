from __future__ import annotations

from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)
from src.application.agent_runtime.streaming.live_event_sink import NullEventSink


def test_null_sink_absorbs_any_event():
    sink = NullEventSink()
    for event_type in LiveAgentEventType:
        sink.emit(LiveAgentEvent(event_type=event_type, payload={"key": "value"}))


def test_null_sink_does_not_raise():
    sink = NullEventSink()
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.ERROR, payload={"message": "oops"}))


def test_null_sink_accepts_empty_payload():
    sink = NullEventSink()
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.RUN_STARTED))

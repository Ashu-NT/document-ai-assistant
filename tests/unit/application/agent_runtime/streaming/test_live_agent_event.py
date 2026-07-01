from __future__ import annotations

from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)


def test_event_creation_with_defaults():
    event = LiveAgentEvent(event_type=LiveAgentEventType.RUN_STARTED)
    assert event.event_type == LiveAgentEventType.RUN_STARTED
    assert event.payload == {}


def test_event_creation_with_payload():
    event = LiveAgentEvent(
        event_type=LiveAgentEventType.UNDERSTAND_REQUEST,
        payload={"route": "answer_question"},
    )
    assert event.payload["route"] == "answer_question"


def test_all_event_types_are_strings():
    for event_type in LiveAgentEventType:
        assert isinstance(event_type.value, str)


def test_event_type_values_are_snake_case():
    for event_type in LiveAgentEventType:
        assert event_type.value == event_type.value.lower()
        assert " " not in event_type.value


def test_event_type_count():
    assert len(LiveAgentEventType) == 16

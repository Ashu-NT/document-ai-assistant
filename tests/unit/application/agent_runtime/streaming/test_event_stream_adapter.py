from __future__ import annotations

from src.application.agent_runtime.streaming.event_stream_adapter import EventStreamAdapter
from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)
from src.application.agent_runtime.streaming.live_event_sink import NullEventSink


class _CollectingSink:
    def __init__(self):
        self.events: list[LiveAgentEvent] = []

    def emit(self, event: LiveAgentEvent) -> None:
        self.events.append(event)


class _FakeCompiledGraph:
    def __init__(self, chunks: list[dict]):
        self._chunks = chunks

    def stream(self, initial_state: dict):
        for chunk in self._chunks:
            yield chunk


def test_adapter_returns_merged_state():
    graph = _FakeCompiledGraph([
        {"route_request": {"route": "answer_question"}},
        {"answer_question": {"answer": "42"}},
    ])
    sink = NullEventSink()
    adapter = EventStreamAdapter(sink)
    result = adapter.run(graph, {"user_input": "test"})
    assert result["route"] == "answer_question"
    assert result["answer"] == "42"


def test_adapter_emits_understand_request_for_route_node():
    graph = _FakeCompiledGraph([
        {"route_request": {"route": "answer_question"}},
    ])
    sink = _CollectingSink()
    adapter = EventStreamAdapter(sink)
    adapter.run(graph, {})
    assert any(e.event_type == LiveAgentEventType.UNDERSTAND_REQUEST for e in sink.events)


def test_adapter_emits_plan_completed_for_research_plan_node():
    graph = _FakeCompiledGraph([
        {"create_research_plan": {"research_plan": {"tasks": [{"title": "t1"}, {"title": "t2"}]}}},
    ])
    sink = _CollectingSink()
    adapter = EventStreamAdapter(sink)
    adapter.run(graph, {})
    plan_events = [e for e in sink.events if e.event_type == LiveAgentEventType.PLAN_COMPLETED]
    assert len(plan_events) == 1
    assert plan_events[0].payload["task_count"] == 2


def test_adapter_emits_reflection_completed_for_reflect_node():
    graph = _FakeCompiledGraph([
        {"reflect_answer": {"reflection_decision": "ACCEPT"}},
    ])
    sink = _CollectingSink()
    adapter = EventStreamAdapter(sink)
    adapter.run(graph, {})
    reflection_events = [e for e in sink.events if e.event_type == LiveAgentEventType.REFLECTION_COMPLETED]
    assert len(reflection_events) == 1
    assert reflection_events[0].payload["decision"] == "ACCEPT"


def test_adapter_emits_blocked_for_blocked_action_node():
    graph = _FakeCompiledGraph([
        {"blocked_action": {"blocked_reason": "unsafe"}},
    ])
    sink = _CollectingSink()
    adapter = EventStreamAdapter(sink)
    adapter.run(graph, {})
    blocked_events = [e for e in sink.events if e.event_type == LiveAgentEventType.BLOCKED]
    assert len(blocked_events) == 1
    assert "unsafe" in blocked_events[0].payload["reason"]


def test_adapter_ignores_unmapped_nodes():
    graph = _FakeCompiledGraph([
        {"some_internal_node": {"internal_key": "value"}},
    ])
    sink = _CollectingSink()
    adapter = EventStreamAdapter(sink)
    adapter.run(graph, {})
    assert len(sink.events) == 0


def test_adapter_accumulates_state_across_nodes():
    graph = _FakeCompiledGraph([
        {"route_request": {"route": "answer_question"}},
        {"retrieve_evidence": {"context_chunks": ["c1", "c2", "c3"]}},
    ])
    sink = _CollectingSink()
    adapter = EventStreamAdapter(sink)
    final = adapter.run(graph, {})
    assert final["route"] == "answer_question"
    assert len(final["context_chunks"]) == 3


def test_adapter_action_completed_includes_chunk_count():
    graph = _FakeCompiledGraph([
        {"retrieve_evidence": {"context_chunks": ["a", "b"]}},
    ])
    sink = _CollectingSink()
    adapter = EventStreamAdapter(sink)
    adapter.run(graph, {})
    action_events = [e for e in sink.events if e.event_type == LiveAgentEventType.ACTION_COMPLETED]
    assert action_events[0].payload["chunk_count"] == 2

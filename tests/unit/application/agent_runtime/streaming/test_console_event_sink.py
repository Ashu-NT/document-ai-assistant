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


def _emit(event_type: LiveAgentEventType, payload: dict | None = None) -> str:
    sink, stream = _sink()
    sink.emit(LiveAgentEvent(event_type=event_type, payload=payload or {}))
    return stream.getvalue()


def test_run_started_prints_agent_loop_header():
    output = _emit(LiveAgentEventType.RUN_STARTED)
    assert "Agent Loop" in output
    assert "----------" in output


def test_understand_request_prints_numbered_step():
    output = _emit(LiveAgentEventType.UNDERSTAND_REQUEST, {"route": "answer_question"})
    assert "[1] Understand" in output


def test_understand_request_humanizes_route():
    output = _emit(LiveAgentEventType.UNDERSTAND_REQUEST, {"route": "answer_question"})
    assert "answer question" in output


def test_action_completed_prints_numbered_retrieve_step():
    output = _emit(LiveAgentEventType.ACTION_COMPLETED)
    assert "[1] Retrieve" in output


def test_action_completed_shows_description():
    output = _emit(
        LiveAgentEventType.ACTION_COMPLETED,
        {"description": "Retrieved 5 evidence chunk(s)."},
    )
    assert "Retrieved 5 evidence chunk(s)." in output


def test_observation_prints_indented_observation_block():
    output = _emit(LiveAgentEventType.OBSERVATION, {"detail": "Synthesis complete."})
    assert "Observation" in output
    assert "Synthesis complete." in output


def test_observation_has_no_step_number():
    output = _emit(LiveAgentEventType.OBSERVATION, {"detail": "Found evidence."})
    lines = [l for l in output.splitlines() if "Observation" in l]
    assert lines
    assert not any(l.strip().startswith("[") for l in lines)


def test_reflection_completed_prints_numbered_reflect_step():
    output = _emit(LiveAgentEventType.REFLECTION_COMPLETED, {"decision": "ACCEPT"})
    assert "[1] Reflect" in output


def test_reflection_shows_decision_and_reason():
    output = _emit(
        LiveAgentEventType.REFLECTION_COMPLETED,
        {"decision": "ACCEPT", "reason": "Grounded in evidence."},
    )
    assert "Decision: ACCEPT" in output
    assert "Grounded in evidence." in output


def test_plan_completed_prints_numbered_plan_step():
    output = _emit(LiveAgentEventType.PLAN_COMPLETED, {"task_titles": ["Task 1"]})
    assert "[1] Plan" in output


def test_plan_shows_task_titles():
    output = _emit(
        LiveAgentEventType.PLAN_COMPLETED,
        {"task_titles": ["Collect maintenance data", "Collect specs"]},
    )
    assert "Collect maintenance data" in output
    assert "Collect specs" in output


def test_plan_falls_back_to_task_count():
    output = _emit(LiveAgentEventType.PLAN_COMPLETED, {"task_count": 3})
    assert "3 task(s)" in output


def test_blocked_prints_numbered_guardrail_step():
    output = _emit(LiveAgentEventType.BLOCKED, {"reason": "Unsafe request."})
    assert "Guardrail" in output
    assert "Unsafe request." in output


def test_final_started_is_silent():
    assert _emit(LiveAgentEventType.FINAL_STARTED) == ""


def test_final_completed_is_silent():
    assert _emit(LiveAgentEventType.FINAL_COMPLETED) == ""


def test_step_counter_increments_across_events():
    stream = io.StringIO()
    sink = ConsoleLiveEventSink(stream=stream)
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.UNDERSTAND_REQUEST, payload={}))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.ACTION_COMPLETED, payload={}))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.REFLECTION_COMPLETED, payload={}))
    output = stream.getvalue()
    assert "[1]" in output
    assert "[2]" in output
    assert "[3]" in output


def test_observation_with_evaluate_kind_prints_evaluate_label():
    output = _emit(LiveAgentEventType.OBSERVATION, {"kind": "evaluate", "detail": "Coverage: 67% — gap: troubleshooting."})
    assert "Evaluate" in output
    assert "Coverage: 67%" in output
    assert "Observation" not in output


def test_observation_with_observation_kind_prints_observation_label():
    output = _emit(LiveAgentEventType.OBSERVATION, {"kind": "observation", "detail": "Synthesis complete."})
    assert "Observation" in output
    assert "Evaluate" not in output


def test_observation_without_kind_defaults_to_observation_label():
    output = _emit(LiveAgentEventType.OBSERVATION, {"detail": "Evidence gathered."})
    assert "Observation" in output
    assert "Evaluate" not in output


def test_header_printed_only_once_across_multiple_events():
    stream = io.StringIO()
    sink = ConsoleLiveEventSink(stream=stream)
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.RUN_STARTED))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.UNDERSTAND_REQUEST, payload={}))
    sink.emit(LiveAgentEvent(event_type=LiveAgentEventType.ACTION_COMPLETED, payload={}))
    output = stream.getvalue()
    assert output.count("Agent Loop") == 1

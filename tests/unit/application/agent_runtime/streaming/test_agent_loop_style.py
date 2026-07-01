"""Integration-style tests for the agent loop terminal presentation format.

Verifies the exact numbered-step structure, header, silence rules, and
ReactPresenter title produced by ConsoleLiveEventSink and ReactPresenter.
"""

from __future__ import annotations

import io

from src.application.agent_runtime.policies.demo_visibility_policy import DemoVisibilityPolicy
from src.application.agent_runtime.react_loop.react_event import ReactEvent
from src.application.agent_runtime.react_loop.react_presenter import ReactPresenter
from src.application.agent_runtime.react_loop.react_step import ReactStep
from src.application.agent_runtime.react_loop.react_trace import ReactTrace
from src.application.agent_runtime.streaming.console_event_sink import ConsoleLiveEventSink
from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)


def _run_sink(*events: tuple[LiveAgentEventType, dict]) -> str:
    stream = io.StringIO()
    sink = ConsoleLiveEventSink(stream=stream)
    for event_type, payload in events:
        sink.emit(LiveAgentEvent(event_type=event_type, payload=payload))
    return stream.getvalue()


def _trace_with_step(title: str, body: str) -> ReactTrace:
    trace = ReactTrace(route="answer_question")
    trace.steps.append(
        ReactStep(
            index=1,
            event_type=ReactEvent.THOUGHT_SUMMARY,
            title=title,
            body=body,
        )
    )
    return trace


# 1. Header is printed exactly once at the start
def test_agent_loop_header_printed_once():
    output = _run_sink(
        (LiveAgentEventType.RUN_STARTED, {}),
        (LiveAgentEventType.UNDERSTAND_REQUEST, {"route": "answer_question"}),
    )
    assert output.count("Agent Loop") == 1
    assert output.count("----------") == 1


# 2. Understand step is [1]
def test_understand_is_step_one():
    output = _run_sink((LiveAgentEventType.UNDERSTAND_REQUEST, {"route": "answer_question"}))
    assert "[1] Understand" in output


# 3. Retrieve step follows Understand with incremented counter
def test_retrieve_step_follows_understand():
    output = _run_sink(
        (LiveAgentEventType.UNDERSTAND_REQUEST, {}),
        (LiveAgentEventType.ACTION_COMPLETED, {}),
    )
    assert "[1] Understand" in output
    assert "[2] Retrieve" in output


# 4. Observation block has no step number
def test_observation_has_no_step_number():
    output = _run_sink((LiveAgentEventType.OBSERVATION, {"detail": "Found evidence."}))
    assert "Observation" in output
    observation_lines = [l for l in output.splitlines() if "Observation" in l]
    assert not any(l.strip().startswith("[") for l in observation_lines)


# 5. Reflect step receives the next counter after Retrieve
def test_reflect_step_numbered_after_retrieve():
    output = _run_sink(
        (LiveAgentEventType.UNDERSTAND_REQUEST, {}),
        (LiveAgentEventType.ACTION_COMPLETED, {}),
        (LiveAgentEventType.REFLECTION_COMPLETED, {"decision": "ACCEPT"}),
    )
    assert "[1] Understand" in output
    assert "[2] Retrieve" in output
    assert "[3] Reflect" in output


# 6. Reflect step shows "Decision:" label
def test_reflect_shows_decision_label():
    output = _run_sink(
        (LiveAgentEventType.REFLECTION_COMPLETED, {"decision": "ACCEPT", "reason": "Grounded."})
    )
    assert "Decision: ACCEPT" in output


# 7. Reflect step shows the reason text
def test_reflect_shows_reason():
    output = _run_sink(
        (LiveAgentEventType.REFLECTION_COMPLETED, {"decision": "FAIL", "reason": "Insufficient evidence."})
    )
    assert "Insufficient evidence." in output


# 8. Plan step shows numbered task titles
def test_plan_step_shows_task_titles():
    output = _run_sink(
        (LiveAgentEventType.PLAN_COMPLETED, {
            "task_count": 2,
            "task_titles": ["Collect maintenance intervals", "Collect oil specs"],
        })
    )
    assert "Plan" in output
    assert "Collect maintenance intervals" in output
    assert "Collect oil specs" in output


# 9. Multiple Retrieve steps each get a unique sequential counter
def test_multiple_retrieve_steps_get_unique_counters():
    output = _run_sink(
        (LiveAgentEventType.ACTION_COMPLETED, {"description": "First retrieval."}),
        (LiveAgentEventType.ACTION_COMPLETED, {"description": "Second retrieval."}),
    )
    assert "[1] Retrieve" in output
    assert "[2] Retrieve" in output


# 10. FINAL_STARTED produces no terminal output
def test_final_started_produces_no_output():
    output = _run_sink((LiveAgentEventType.FINAL_STARTED, {}))
    assert output == ""


# 11. FINAL_COMPLETED produces no terminal output
def test_final_completed_produces_no_output():
    output = _run_sink((LiveAgentEventType.FINAL_COMPLETED, {}))
    assert output == ""


# 12. BLOCKED produces a Guardrail step with the reason
def test_guardrail_shows_reason():
    output = _run_sink(
        (LiveAgentEventType.BLOCKED, {"reason": "Destructive corpus operation refused."})
    )
    assert "Guardrail" in output
    assert "Destructive corpus operation refused." in output


# 13. ERROR is displayed inline without a step number
def test_error_displayed_without_step_number():
    output = _run_sink((LiveAgentEventType.ERROR, {"message": "Graph execution failed."}))
    assert "Graph execution failed." in output
    assert "[1] Error" not in output
    assert "[1]" not in output


# 14. ReactPresenter keeps "Agent Trace" title — distinct from the streaming "Agent Loop" header
#     so the two sections don't appear duplicated when --show-react is enabled
def test_react_presenter_title_is_agent_trace_not_loop():
    trace = _trace_with_step(
        "Thought Summary",
        "The request asks for document evidence.",
    )
    rendered = ReactPresenter().render(trace, policy=DemoVisibilityPolicy())
    assert "Agent Trace" in rendered
    assert "Agent Loop" not in rendered


# 15. Deep research loop: Evaluate block appears between Retrieve iterations
def test_deep_research_loop_shows_evaluate_between_retrieve_steps():
    output = _run_sink(
        (LiveAgentEventType.UNDERSTAND_REQUEST, {"route": "deep_research"}),
        (LiveAgentEventType.PLAN_COMPLETED, {"task_titles": ["Collect maintenance data"]}),
        (LiveAgentEventType.ACTION_COMPLETED, {"description": "Retrieved 8 evidence chunk(s)."}),
        (LiveAgentEventType.OBSERVATION, {"kind": "evaluate", "detail": "Coverage: 67% — gap: troubleshooting — running follow-up retrieval."}),
        (LiveAgentEventType.ACTION_COMPLETED, {"description": "Retrieved 4 evidence chunk(s)."}),
        (LiveAgentEventType.OBSERVATION, {"kind": "evaluate", "detail": "Coverage: 100% — moving to synthesis."}),
        (LiveAgentEventType.OBSERVATION, {"kind": "observation", "detail": "Synthesis complete."}),
    )
    assert "Evaluate" in output
    assert "Coverage: 67%" in output
    assert "running follow-up retrieval" in output
    assert "Coverage: 100%" in output
    assert "Observation" in output
    assert "Synthesis complete." in output
    # Evaluate must appear before the second Retrieve
    assert output.index("Coverage: 67%") < output.index("Coverage: 100%")

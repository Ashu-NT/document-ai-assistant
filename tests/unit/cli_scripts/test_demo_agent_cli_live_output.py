from __future__ import annotations

import io
import threading
import time

from src.application.agent_runtime.progress.thinking_animation import ThinkingAnimation


def _run_animation(stages: list[str], run_seconds: float) -> list[str]:
    stream = io.StringIO()
    anim = ThinkingAnimation(stream=stream, interval_seconds=0.05)
    running = anim.start(stages)
    time.sleep(run_seconds)
    running.stop(success=True)
    return stream.getvalue().splitlines()


def test_each_stage_printed_at_most_once():
    stages = ["Routing request", "Retrieving evidence", "Finalizing response"]
    # Run for 0.5s with 0.05s interval — enough to exhaust all stages and then idle
    lines = _run_animation(stages, run_seconds=0.5)
    content_lines = [l for l in lines if l.strip() and not l.strip().startswith("[")]
    for stage in stages:
        count = sum(1 for l in content_lines if stage in l)
        assert count <= 1, f"Stage '{stage}' appeared {count} times — expected at most 1"


def test_last_stage_not_repeated():
    stages = ["A", "B", "C"]
    lines = _run_animation(stages, run_seconds=0.5)
    content_lines = [l for l in lines if "C" in l and not l.startswith("[")]
    assert len(content_lines) <= 1, f"Last stage 'C' repeated {len(content_lines)} times"


def test_all_stages_appear_when_graph_is_slow():
    stages = ["Stage1", "Stage2", "Stage3"]
    # interval 0.05s * 3 = 0.15s to cycle through all; run for 0.3s
    lines = _run_animation(stages, run_seconds=0.3)
    content_lines = [l for l in lines if any(s in l for s in stages)]
    seen = {s for s in stages if any(s in l for l in content_lines)}
    assert seen == set(stages), f"Not all stages appeared. Seen: {seen}"


def test_stages_appear_in_order():
    stages = ["Alpha", "Beta", "Gamma"]
    lines = _run_animation(stages, run_seconds=0.3)
    content_lines = [l for l in lines if any(s in l for s in stages)]
    order = []
    for line in content_lines:
        for stage in stages:
            if stage in line:
                order.append(stage)
                break
    for i, s in enumerate(order):
        assert s == stages[i], f"Expected stage {stages[i]} at position {i}, got {s}"


def test_animation_ends_cleanly():
    stages = ["Routing request"]
    stream = io.StringIO()
    anim = ThinkingAnimation(stream=stream, interval_seconds=0.05)
    running = anim.start(stages)
    time.sleep(0.2)
    running.stop(success=True)
    output = stream.getvalue()
    assert "[ok]" in output


def test_fail_marker_on_failure():
    stages = ["Routing request"]
    stream = io.StringIO()
    anim = ThinkingAnimation(stream=stream, interval_seconds=0.05)
    running = anim.start(stages)
    time.sleep(0.1)
    running.stop(success=False)
    output = stream.getvalue()
    assert "[failed]" in output


def test_empty_stages_does_not_print():
    stream = io.StringIO()
    anim = ThinkingAnimation(stream=stream, interval_seconds=0.05)
    running = anim.start([])
    time.sleep(0.1)
    running.stop(success=True)
    output = stream.getvalue()
    assert output.strip() == ""

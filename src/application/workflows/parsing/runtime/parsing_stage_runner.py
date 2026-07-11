import time
from collections.abc import Callable
from typing import TypeVar

from src.application.workflows.parsing.runtime.parsing_stage_heartbeat import (
    StageHeartbeat,
)
from src.shared.formatting.duration_formatter import format_elapsed_seconds
from src.shared.progress.progress_emitter import emit_progress

T = TypeVar("T")


def run_stage(
    *,
    progress_callback: Callable[[str], None] | None,
    start_message: str,
    heartbeat_label: str,
    failure_label: str,
    operation: Callable[[], T],
    completion_message_builder: Callable[[T, float], str],
    stage_name: str | None = None,
    stage_durations: dict[str, float] | None = None,
) -> T:
    emit_progress(progress_callback, start_message)
    started_at = time.perf_counter()
    heartbeat = StageHeartbeat(
        label=heartbeat_label,
        progress_callback=progress_callback,
    )
    heartbeat.start()
    try:
        result = operation()
    except Exception:
        elapsed_seconds = time.perf_counter() - started_at
        emit_progress(
            progress_callback,
            f"{failure_label} failed after "
            f"{format_elapsed_seconds(elapsed_seconds)}.",
        )
        raise
    finally:
        heartbeat.stop()

    elapsed_seconds = time.perf_counter() - started_at
    if stage_name is not None and stage_durations is not None:
        stage_durations[stage_name] = elapsed_seconds
    emit_progress(
        progress_callback,
        completion_message_builder(result, elapsed_seconds),
    )
    return result

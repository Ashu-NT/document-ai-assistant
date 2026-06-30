from __future__ import annotations

import sys
from typing import Callable, TypeVar

from src.application.agent_runtime.progress.thinking_animation import ThinkingAnimation

T = TypeVar("T")


class ProgressIndicator:
    def __init__(
        self,
        *,
        enabled: bool,
        stream=None,
        interval_seconds: float = 1.0,
    ) -> None:
        self.enabled = enabled
        self.stream = stream or sys.stdout
        self.interval_seconds = interval_seconds

    def run_with_progress(
        self,
        stages: list[str],
        action: Callable[[], T],
    ) -> T:
        if not self.enabled or not stages:
            return action()
        animation = ThinkingAnimation(
            stream=self.stream,
            interval_seconds=self.interval_seconds,
        )
        running = animation.start(stages)
        try:
            result = action()
        except Exception:
            running.stop(success=False)
            raise
        running.stop(success=True)
        return result

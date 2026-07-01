from __future__ import annotations

import threading
from time import sleep
from typing import TextIO


class ThinkingAnimation:
    def __init__(
        self,
        *,
        stream: TextIO,
        interval_seconds: float = 1.0,
    ) -> None:
        self.stream = stream
        self.interval_seconds = interval_seconds

    def start(self, stages: list[str]) -> "_RunningAnimation":
        running = _RunningAnimation(
            stream=self.stream,
            stages=stages,
            interval_seconds=self.interval_seconds,
        )
        running.start()
        return running


class _RunningAnimation:
    def __init__(
        self,
        *,
        stream: TextIO,
        stages: list[str],
        interval_seconds: float,
    ) -> None:
        self.stream = stream
        self.stages = stages
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._last_stage: str | None = None

    def start(self) -> None:
        self._thread.start()

    def stop(self, *, success: bool) -> None:
        self._stop_event.set()
        self._thread.join(timeout=self.interval_seconds + 0.5)
        if self._last_stage:
            marker = "[ok]" if success else "[failed]"
            print(f"{marker}", file=self.stream, flush=True)

    def _run(self) -> None:
        if not self.stages:
            return
        index = 0
        while not self._stop_event.is_set():
            if index < len(self.stages):
                self._last_stage = self.stages[index]
                print(f"{self._last_stage}...", file=self.stream, flush=True)
                index += 1
            if self._stop_event.wait(self.interval_seconds):
                return

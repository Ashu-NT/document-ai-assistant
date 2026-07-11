import time
from collections.abc import Callable
from threading import Event, Thread

from src.shared.formatting.duration_formatter import format_elapsed_seconds

STAGE_HEARTBEAT_INTERVAL_SECONDS = 30.0


class StageHeartbeat:
    def __init__(
        self,
        *,
        label: str,
        progress_callback: Callable[[str], None] | None,
        interval_seconds: float = STAGE_HEARTBEAT_INTERVAL_SECONDS,
    ) -> None:
        self.label = label
        self.progress_callback = progress_callback
        self.interval_seconds = interval_seconds
        self._started_at = 0.0
        self._stop_event = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        if self.progress_callback is None or self._thread is not None:
            return

        self._started_at = time.perf_counter()
        self._thread = Thread(
            target=self._run,
            name="parsing-stage-heartbeat",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return

        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=0.1)

    def _run(self) -> None:
        while not self._stop_event.wait(self.interval_seconds):
            elapsed_seconds = time.perf_counter() - self._started_at
            self.progress_callback(
                f"{self.label} still running... "
                f"({format_elapsed_seconds(elapsed_seconds)} elapsed)"
            )

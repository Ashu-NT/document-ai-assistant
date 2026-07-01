from __future__ import annotations

from typing import Protocol

from src.application.agent_runtime.streaming.live_agent_event import LiveAgentEvent


class LiveEventSink(Protocol):
    def emit(self, event: LiveAgentEvent) -> None: ...


class NullEventSink:
    def emit(self, event: LiveAgentEvent) -> None:
        pass

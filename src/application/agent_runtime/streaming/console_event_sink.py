from __future__ import annotations

import sys
from typing import Any, TextIO

from src.application.agent_runtime.streaming.live_agent_event import (
    LiveAgentEvent,
    LiveAgentEventType,
)

_SILENT: frozenset[LiveAgentEventType] = frozenset({
    LiveAgentEventType.RUN_COMPLETED,
    LiveAgentEventType.FINAL_STARTED,
    LiveAgentEventType.FINAL_COMPLETED,
    LiveAgentEventType.STRATEGY_STARTED,
    LiveAgentEventType.STRATEGY_COMPLETED,
    LiveAgentEventType.PLAN_STARTED,
    LiveAgentEventType.ACTION_STARTED,
    LiveAgentEventType.REFLECTION_STARTED,
})


class ConsoleLiveEventSink:
    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = stream or sys.stdout
        self._step = 0
        self._header_printed = False

    def emit(self, event: LiveAgentEvent) -> None:
        t = event.event_type
        p: dict[str, Any] = event.payload or {}

        if t in _SILENT:
            return

        if t == LiveAgentEventType.RUN_STARTED:
            self._ensure_header()
            return

        if t == LiveAgentEventType.UNDERSTAND_REQUEST:
            self._ensure_header()
            n = self._next_step()
            route = str(p.get("route") or "").replace("_", " ").strip()
            self._println(f"\n[{n}] Understand")
            if route:
                self._println(f"    Route → {route}")
            return

        if t == LiveAgentEventType.PLAN_COMPLETED:
            self._ensure_header()
            n = self._next_step()
            titles: list[str] = p.get("task_titles") or []
            task_count: int = p.get("task_count") or 0
            self._println(f"\n[{n}] Plan")
            if titles:
                for i, title in enumerate(titles, 1):
                    self._println(f"    {i}. {title}")
            elif task_count:
                self._println(f"    {task_count} task(s)")
            return

        if t == LiveAgentEventType.ACTION_COMPLETED:
            self._ensure_header()
            n = self._next_step()
            description = str(p.get("description") or "").strip()
            self._println(f"\n[{n}] Retrieve")
            if description:
                self._println(f"    {description}")
            return

        if t == LiveAgentEventType.OBSERVATION:
            kind = str(p.get("kind") or "").strip()
            detail = str(p.get("detail") or "").strip()
            label = "Evaluate" if kind == "evaluate" else "Observation"
            self._println(f"\n    {label}")
            if detail:
                self._println(f"    {detail}")
            return

        if t == LiveAgentEventType.REFLECTION_COMPLETED:
            self._ensure_header()
            n = self._next_step()
            decision = str(p.get("decision") or "").strip()
            reason = str(p.get("reason") or "").strip()
            self._println(f"\n[{n}] Reflect")
            if decision:
                self._println(f"    Decision: {decision}")
            if reason:
                self._println(f"    {reason}")
            return

        if t == LiveAgentEventType.BLOCKED:
            self._ensure_header()
            n = self._next_step()
            reason = str(p.get("reason") or "").strip()
            self._println(f"\n[{n}] Guardrail")
            if reason:
                self._println(f"    {reason}")
            return

        if t == LiveAgentEventType.ERROR:
            message = str(p.get("message") or "").strip()
            self._println(f"\n    Error: {message}")
            return

    def _ensure_header(self) -> None:
        if not self._header_printed:
            self._header_printed = True
            print("Agent Loop", file=self._stream, flush=True)
            print("----------", file=self._stream, flush=True)

    def _next_step(self) -> int:
        self._step += 1
        return self._step

    def _println(self, text: str) -> None:
        print(text, file=self._stream, flush=True)

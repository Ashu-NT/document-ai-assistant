from __future__ import annotations

from dataclasses import dataclass, field


_DEFAULT_PROMPT_INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore your instructions",
    "bypass safety",
    "bypass guardrails",
    "show the system prompt",
    "show your system prompt",
    "reveal hidden prompt",
    "reveal hidden instructions",
    "chain of thought",
    "chain-of-thought",
    "hidden prompt",
    "developer message",
)


@dataclass(slots=True, frozen=True)
class PromptInjectionPolicy:
    blocked_markers: tuple[str, ...] = field(
        default_factory=lambda: _DEFAULT_PROMPT_INJECTION_MARKERS
    )

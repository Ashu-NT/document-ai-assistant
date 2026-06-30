from __future__ import annotations

from dataclasses import dataclass, field


_DEFAULT_ALLOWED_SIGNALS = (
    "document",
    "manual",
    "datasheet",
    "certificate",
    "drawing",
    "report",
    "section",
    "page",
    "reference",
    "source",
    "evidence",
    "chunk",
    "table",
    "maintenance",
    "interval",
    "specification",
    "spare parts",
    "part number",
    "serial number",
    "manufacturer",
    "model",
    "pressure",
    "voltage",
    "pump",
    "sensor",
    "device",
    "equipment",
    "component",
    "filter",
    "valve",
    "hydraulic",
    "alarm",
    "replace",
    "install",
    "remove",
    "oil",
    "calibration",
    "warning",
    "procedure",
    "troubleshooting",
)
_DEFAULT_COMMAND_SIGNALS = (
    "list documents",
    "list docs",
    "open ",
    "select ",
    "current document",
    "clear document",
    "help",
    "trace",
    "context",
    "export",
    "benchmark",
    "quality gate",
    "explore",
    "explore document",
    "explore it",
    "show sections",
    "what is in this document",
    "what is in it",
)
_DEFAULT_OUT_OF_SCOPE_SIGNALS = (
    "weather",
    "sports",
    "football",
    "football match",
    "joke",
    "poem",
    "recipe",
    "movie",
    "dating",
    "politics",
    "celebrity",
    "stock price",
    "medical",
    "legal advice",
    "travel booking",
    "capital of france",
)


@dataclass(slots=True, frozen=True)
class DomainScopePolicy:
    allowed_scope_signals: tuple[str, ...] = field(
        default_factory=lambda: _DEFAULT_ALLOWED_SIGNALS
    )
    command_signals: tuple[str, ...] = field(
        default_factory=lambda: _DEFAULT_COMMAND_SIGNALS
    )
    out_of_scope_signals: tuple[str, ...] = field(
        default_factory=lambda: _DEFAULT_OUT_OF_SCOPE_SIGNALS
    )
    minimum_meaningful_words: int = 2

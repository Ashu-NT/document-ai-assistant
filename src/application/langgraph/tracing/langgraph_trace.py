from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class LangGraphTrace:
    node_name: str
    started_at: str
    finished_at: str
    elapsed_ms: float
    route: str | None = None
    success: bool = True
    tool_name: str | None = None
    error_code: str | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_name": self.node_name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "elapsed_ms": self.elapsed_ms,
            "route": self.route,
            "success": self.success,
            "tool_name": self.tool_name,
            "error_code": self.error_code,
            "diagnostics": dict(self.diagnostics),
        }

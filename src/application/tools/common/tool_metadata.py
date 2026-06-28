from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ToolMetadata:
    tool_name: str
    category: str
    version: str = "v1"
    description: str | None = None
    requires_llm: bool = False
    mutates_state: bool = False
    supports_trace: bool = False

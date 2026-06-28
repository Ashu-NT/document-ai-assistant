from __future__ import annotations

from dataclasses import dataclass

from src.application.langgraph.common.graph_constants import (
    DEFAULT_AGENT_GRAPH_NAME,
    DEFAULT_AGENT_GRAPH_VERSION,
)


@dataclass(slots=True, frozen=True)
class GraphMetadata:
    graph_name: str = DEFAULT_AGENT_GRAPH_NAME
    version: str = DEFAULT_AGENT_GRAPH_VERSION
    description: str | None = None
    supports_memory: bool = False
    supports_streaming: bool = False
    deterministic: bool = True

from __future__ import annotations

from src.application.langgraph.graphs import DocumentAgentGraph
from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.factories.tool_registry import ToolRegistry


class GraphFactory:
    def create_document_agent_graph(
        self,
        *,
        tool_registry: ToolRegistry,
        memory: ConversationMemory | None = None,
    ) -> DocumentAgentGraph:
        return DocumentAgentGraph(
            tool_registry=tool_registry,
            memory=memory,
        )

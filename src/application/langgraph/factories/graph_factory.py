from __future__ import annotations

from src.application.langgraph.graphs import DocumentAgentGraph
from src.application.langgraph.memory import ConversationMemory, SessionStateStore
from src.application.langgraph.factories.tool_registry import ToolRegistry


class GraphFactory:
    def create_document_agent_graph(
        self,
        *,
        tool_registry: ToolRegistry,
        memory: ConversationMemory | None = None,
        session_state_store: SessionStateStore | None = None,
    ) -> DocumentAgentGraph:
        effective_memory = memory
        if effective_memory is None and session_state_store is not None:
            effective_memory = ConversationMemory(
                max_messages=20,
                session_state_store=session_state_store,
            )
        return DocumentAgentGraph(
            tool_registry=tool_registry,
            memory=effective_memory,
        )

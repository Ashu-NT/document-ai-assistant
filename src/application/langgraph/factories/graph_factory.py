from __future__ import annotations

from src.application.langgraph.factories.node_factory import NodeFactory
from src.application.langgraph.graphs import DocumentAgentGraph
from src.application.langgraph.memory import ConversationMemory, SessionStateStore
from src.application.langgraph.factories.tool_registry import ToolRegistry


class GraphFactory:
    def __init__(self, *, node_factory: NodeFactory | None = None) -> None:
        self.node_factory = node_factory or NodeFactory()

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
        nodes = self.node_factory.build_document_agent_nodes(
            tool_registry=tool_registry,
            intent_router=DocumentAgentGraph.default_intent_router(),
            memory=effective_memory,
        )
        return DocumentAgentGraph(
            tool_registry=tool_registry,
            memory=effective_memory,
            nodes=nodes,
        )

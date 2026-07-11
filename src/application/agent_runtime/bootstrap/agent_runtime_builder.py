from __future__ import annotations

from src.application.agent_runtime.bootstrap.agent_node_factory_builder import (
    build_agent_node_factory,
)
from src.application.agent_runtime.bootstrap.agent_runtime import (
    AgentRuntime,
    DemoRuntimeStatus,
)
from src.application.agent_runtime.bootstrap.agent_service_builder import (
    build_agent_services,
)
from src.application.agent_runtime.bootstrap.agent_tool_registry_builder import (
    build_agent_tool_registry,
)


def build_agent_runtime(
    session,
    *,
    enable_generation: bool,
    enable_llm_planning: bool,
    enable_llm_research_planning: bool,
) -> AgentRuntime:
    from src.application.langgraph import ConversationMemory, GraphFactory, SessionStateStore
    from src.config.settings import ingestion_settings, langgraph_settings, llm_settings

    services = build_agent_services(
        session,
        enable_generation=enable_generation,
        enable_llm_planning=enable_llm_planning,
        enable_llm_research_planning=enable_llm_research_planning,
    )
    tool_registry = build_agent_tool_registry(services)
    node_factory = build_agent_node_factory(
        services,
        enable_llm_research_planning=enable_llm_research_planning,
    )
    session_state_store = SessionStateStore()
    conversation_memory = ConversationMemory(
        max_messages=20,
        session_state_store=session_state_store,
    )
    graph = GraphFactory(node_factory=node_factory).create_document_agent_graph(
        tool_registry=tool_registry,
        memory=conversation_memory,
    )
    runtime_status = DemoRuntimeStatus(
        document_count=len(services.document_catalog_service.list_documents()),
        embedding_index_status="Ready",
        model_name=llm_settings.general_llm,
        capabilities=[
            "Question Answering",
            "Retrieval-Augmented Generation",
            "Deep Research",
            "Multi-step Planning",
            "Reflection",
            "Retrieval Strategy Selection",
            "Safe Grounded Answers",
        ],
    )
    return AgentRuntime(
        graph=graph,
        session=session,
        qdrant_client=services.qdrant_client,
        conversation_memory=conversation_memory,
        session_state_store=session_state_store,
        document_catalog_service=services.document_catalog_service,
        runtime_status=runtime_status,
        runtime_settings={
            "ollama_base_url": llm_settings.ollama_base_url,
            "general_llm": llm_settings.general_llm,
            "planning_llm": llm_settings.planning_llm or llm_settings.general_llm,
            "answer_generation_llm": llm_settings.answer_generation_llm,
            "deep_research_enabled": langgraph_settings.deep_research_enabled,
            "reflection_enabled": langgraph_settings.reflection_enabled,
            "retrieval_strategy_enabled": langgraph_settings.retrieval_strategy_enabled,
            "generation_enabled": enable_generation or ingestion_settings.enable_answer_generation,
        },
    )

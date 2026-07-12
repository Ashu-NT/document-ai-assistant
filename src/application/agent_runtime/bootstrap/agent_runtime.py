from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.application.langgraph.common import GraphResult


@dataclass(slots=True)
class DemoRuntimeStatus:
    document_count: int = 0
    embedding_index_status: str = "Ready"
    model_name: str | None = None
    capabilities: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AgentRuntime:
    graph: Any
    session: Any = None
    qdrant_client: Any = None
    conversation_memory: Any = None
    session_state_store: Any = None
    document_catalog_service: Any = None
    runtime_status: DemoRuntimeStatus = field(default_factory=DemoRuntimeStatus)
    runtime_settings: dict[str, Any] = field(default_factory=dict)

    def run_graph_request(
        self,
        user_input: str,
        *,
        document_id: str | None,
        document_query: str | None,
        session_id: str | None,
        allow_answer_generation: bool,
        include_context: bool,
        show_raw_evidence: bool = False,
        llm_planning_enabled: bool = False,
        deep_research_enabled: bool = False,
        llm_research_planning_enabled: bool = False,
        show_research_plan: bool = False,
        show_research_trace: bool = False,
        reflection_enabled: bool = False,
        show_reflection: bool = False,
        retrieval_strategy_enabled: bool = False,
        llm_retrieval_strategy_enabled: bool = False,
        show_retrieval_strategy: bool = False,
        requested_retrieval_strategy: str | None = None,
        show_plan: bool = False,
        show_raw_plan: bool = False,
        top_k: int | None = None,
        event_sink: Any = None,
    ) -> GraphResult:
        return self.graph.run(
            user_input,
            document_id=document_id,
            document_query=document_query,
            session_id=session_id,
            allow_answer_generation=allow_answer_generation,
            include_context=include_context,
            show_raw_evidence=show_raw_evidence,
            llm_planning_enabled=llm_planning_enabled,
            deep_research_enabled=deep_research_enabled,
            llm_research_planning_enabled=llm_research_planning_enabled,
            show_research_plan=show_research_plan,
            show_research_trace=show_research_trace,
            reflection_enabled=reflection_enabled,
            show_reflection=show_reflection,
            retrieval_strategy_enabled=retrieval_strategy_enabled,
            llm_retrieval_strategy_enabled=llm_retrieval_strategy_enabled,
            show_retrieval_strategy=show_retrieval_strategy,
            requested_retrieval_strategy=requested_retrieval_strategy,
            show_plan=show_plan,
            show_raw_plan=show_raw_plan,
            top_k=top_k,
            event_sink=event_sink,
        )

    def load_session_snapshot(self, session_id: str | None) -> dict[str, Any]:
        if self.conversation_memory is None:
            return {}
        snapshot = self.conversation_memory.load_session(session_id)
        if isinstance(snapshot, dict):
            return snapshot
        return {}

    def clear_persisted_session(self, session_id: str | None) -> None:
        if self.conversation_memory is None or not session_id:
            return
        self.conversation_memory.clear(session_id)

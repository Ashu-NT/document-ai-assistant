from __future__ import annotations

from typing import Any

from src.application.langgraph.common import GraphMetadata, GraphResult
from src.application.langgraph.factories.node_factory import NodeFactory
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.graphs.document_agent.document_agent_graph_builder import (
    compile_graph,
)
from src.application.langgraph.graphs.document_agent.document_agent_interpreter import (
    build_initial_state,
)
from src.application.langgraph.graphs.document_agent.document_agent_result_builder import (
    build_result,
)
from src.application.langgraph.graphs.document_agent.document_agent_router import (
    next_node_name,
)
from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.routing import IntentRouter, RouteType
from src.application.langgraph.state import AgentState
from src.application.langgraph.validation import (
    GraphRequestValidator,
    GraphStateValidator,
)

try:
    from langgraph.graph import END
except ImportError:  # pragma: no cover
    END = "__end__"


class DocumentAgentGraph:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        memory: ConversationMemory | None = None,
        request_validator: GraphRequestValidator | None = None,
        state_validator: GraphStateValidator | None = None,
        intent_router: IntentRouter | None = None,
        metadata: GraphMetadata | None = None,
        nodes: dict[str, Any] | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.memory = memory
        self.request_validator = request_validator or GraphRequestValidator()
        self.state_validator = state_validator or GraphStateValidator()
        self.intent_router = intent_router or self.default_intent_router()
        self.metadata = metadata or GraphMetadata(
            supports_memory=memory is not None,
        )
        self._nodes = nodes or self._build_nodes()
        self._compiled_graph = compile_graph(self._nodes)

    @staticmethod
    def default_intent_router() -> IntentRouter:
        return IntentRouter()

    def run(
        self,
        user_input: str,
        document_id: str | None = None,
        document_query: str | None = None,
        session_id: str | None = None,
        allow_answer_generation: bool = False,
        include_context: bool = False,
        show_raw_evidence: bool = False,
        llm_planning_enabled: bool = False,
        show_plan: bool = False,
        show_raw_plan: bool = False,
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
        top_k: int | None = None,
        conversation_id: str | None = None,
        event_sink: Any = None,
    ) -> GraphResult:
        initial_state = build_initial_state(
            user_input=user_input,
            document_id=document_id,
            document_query=document_query,
            session_id=session_id,
            allow_answer_generation=allow_answer_generation,
            include_context=include_context,
            show_raw_evidence=show_raw_evidence,
            llm_planning_enabled=llm_planning_enabled,
            show_plan=show_plan,
            show_raw_plan=show_raw_plan,
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
            top_k=top_k,
            conversation_id=conversation_id,
            memory=self.memory,
        )

        validation = self.request_validator.validate(dict(initial_state))
        if not validation.is_valid:
            return GraphResult.fail(
                response_text="Graph request validation failed.",
                error_code="invalid_request",
                diagnostics={
                    "issues": [
                        {
                            "field": issue.field,
                            "message": issue.message,
                            "code": issue.code,
                        }
                        for issue in validation.issues
                    ]
                },
                route=RouteType.UNKNOWN.value,
                messages=initial_state["history"],
            )

        state_validation = self.state_validator.validate(dict(initial_state))
        if not state_validation.is_valid:
            return GraphResult.fail(
                response_text="Graph state validation failed.",
                error_code="invalid_state",
                diagnostics={
                    "issues": [
                        {
                            "field": issue.field,
                            "message": issue.message,
                            "code": issue.code,
                        }
                        for issue in state_validation.issues
                    ]
                },
                route=RouteType.UNKNOWN.value,
                messages=initial_state["history"],
            )

        if self.memory is not None:
            self.memory.append_user_message(
                user_input,
                conversation_id=initial_state["session_id"],
            )
            initial_state["history"] = self.memory.get_history()

        final_state = self._invoke(initial_state, event_sink=event_sink)
        response_text = final_state.get("response_text")
        if self.memory is not None and response_text:
            self.memory.append_assistant_message(
                response_text,
                conversation_id=initial_state["session_id"],
            )
            final_state["history"] = self.memory.get_history()

        return build_result(final_state)

    def _build_nodes(self) -> dict[str, Any]:
        node_factory = NodeFactory()
        return node_factory.build_document_agent_nodes(
            tool_registry=self.tool_registry,
            intent_router=self.intent_router,
            memory=self.memory,
        )

    def _invoke(self, initial_state: AgentState, event_sink: Any = None) -> AgentState:
        if self._compiled_graph is not None:
            if event_sink is not None:
                from src.application.agent_runtime.streaming.event_stream_adapter import (
                    EventStreamAdapter,
                )
                return EventStreamAdapter(event_sink).run(
                    self._compiled_graph, dict(initial_state)
                )  # type: ignore[return-value]
            return self._compiled_graph.invoke(initial_state)

        state: AgentState = dict(initial_state)  # type: ignore[assignment]
        next_node = "route_request"
        while next_node != END:
            patch = self._nodes[next_node](state)
            state = self._merge_state(state, patch)
            next_node = next_node_name(next_node, state)
        return state

    @staticmethod
    def _merge_state(state: AgentState, patch: dict[str, Any]) -> AgentState:
        merged = dict(state)
        merged.update(patch)
        return merged  # type: ignore[return-value]

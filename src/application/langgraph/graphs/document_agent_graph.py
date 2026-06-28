from __future__ import annotations

from typing import Any

from src.application.langgraph.common import GraphMetadata, GraphResult
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.nodes import (
    AnswerQuestionNode,
    ClarifyRequestNode,
    DocumentDetailsNode,
    ErrorHandlerNode,
    ExploreDocumentNode,
    FinalResponseNode,
    FindDocumentNode,
    ListDocumentsNode,
    RetrievalTraceNode,
    RetrieveEvidenceNode,
    RouteRequestNode,
    RunQualityGateNode,
)
from src.application.langgraph.routing import IntentRouter, RouteType
from src.application.langgraph.state import AgentState, build_agent_state
from src.application.langgraph.validation import GraphRequestValidator

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:  # pragma: no cover
    END = "__end__"
    START = "__start__"
    StateGraph = None


class DocumentAgentGraph:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        memory: ConversationMemory | None = None,
        request_validator: GraphRequestValidator | None = None,
        intent_router: IntentRouter | None = None,
        metadata: GraphMetadata | None = None,
    ) -> None:
        self.tool_registry = tool_registry
        self.memory = memory
        self.request_validator = request_validator or GraphRequestValidator()
        self.intent_router = intent_router or IntentRouter()
        self.metadata = metadata or GraphMetadata(
            supports_memory=memory is not None,
        )
        self._nodes = self._build_nodes()
        self._compiled_graph = self._compile_graph()

    def run(
        self,
        user_input: str,
        **options: Any,
    ) -> GraphResult:
        initial_state = build_agent_state(
            user_input=user_input,
            document_id=options.get("document_id"),
            document_query=options.get("document_query"),
            allow_answer_generation=options.get("allow_answer_generation", False),
            include_context=options.get("include_context", False),
            top_k=options.get("top_k"),
            conversation_id=options.get("conversation_id"),
            history=self.memory.get_history() if self.memory is not None else [],
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

        if self.memory is not None:
            self.memory.append_user_message(
                user_input,
                conversation_id=initial_state["conversation_id"],
            )
            initial_state["history"] = self.memory.get_history()

        final_state = self._invoke(initial_state)
        response_text = final_state.get("response_text")
        if self.memory is not None and response_text:
            self.memory.append_assistant_message(
                response_text,
                conversation_id=initial_state["conversation_id"],
            )
            final_state["history"] = self.memory.get_history()

        return self._build_result(final_state)

    def _build_nodes(self) -> dict[str, Any]:
        return {
            "route_request": RouteRequestNode(self.intent_router),
            "list_documents": ListDocumentsNode(self.tool_registry),
            "find_document": FindDocumentNode(self.tool_registry),
            "document_details": DocumentDetailsNode(self.tool_registry),
            "explore_document": ExploreDocumentNode(self.tool_registry),
            "retrieve_evidence": RetrieveEvidenceNode(self.tool_registry),
            "answer_question": AnswerQuestionNode(self.tool_registry),
            "run_quality_gate": RunQualityGateNode(self.tool_registry),
            "retrieval_trace": RetrievalTraceNode(self.tool_registry),
            "clarify_request": ClarifyRequestNode(),
            "error_handler": ErrorHandlerNode(),
            "final_response": FinalResponseNode(),
        }

    def _compile_graph(self):
        if StateGraph is None:
            return None

        graph = StateGraph(AgentState)
        for node_name, node in self._nodes.items():
            graph.add_node(node_name, node)

        graph.add_edge(START, "route_request")
        graph.add_conditional_edges(
            "route_request",
            self._entry_branch,
            {
                "list_documents": "list_documents",
                "find_document": "find_document",
                "document_details": "document_details",
                "explore_document": "explore_document",
                "retrieve_evidence": "retrieve_evidence",
                "answer_question": "answer_question",
                "run_quality_gate": "run_quality_gate",
                "retrieval_trace": "retrieval_trace",
                "clarify_request": "clarify_request",
            },
        )
        graph.add_conditional_edges(
            "find_document",
            self._after_find_document_branch,
            {
                "document_details": "document_details",
                "explore_document": "explore_document",
                "retrieve_evidence": "retrieve_evidence",
                "answer_question": "answer_question",
                "final_response": "final_response",
                "clarify_request": "clarify_request",
                "error_handler": "error_handler",
                "retrieval_trace": "retrieval_trace",
            },
        )
        for action_node in (
            "list_documents",
            "document_details",
            "explore_document",
            "retrieve_evidence",
            "answer_question",
            "run_quality_gate",
            "retrieval_trace",
        ):
            graph.add_conditional_edges(
                action_node,
                self._post_action_branch,
                {
                    "final_response": "final_response",
                    "clarify_request": "clarify_request",
                    "error_handler": "error_handler",
                },
            )

        graph.add_edge("clarify_request", "final_response")
        graph.add_edge("error_handler", "final_response")
        graph.add_edge("final_response", END)
        return graph.compile()

    def _invoke(self, initial_state: AgentState) -> AgentState:
        if self._compiled_graph is not None:
            return self._compiled_graph.invoke(initial_state)

        state: AgentState = dict(initial_state)  # type: ignore[assignment]
        next_node = "route_request"
        while next_node != END:
            patch = self._nodes[next_node](state)
            state = self._merge_state(state, patch)
            next_node = self._next_node_name(next_node, state)
        return state

    def _build_result(self, state: AgentState) -> GraphResult:
        route = state.get("route")
        diagnostics = {
            "needs_clarification": state.get("needs_clarification", False),
            "configured_tools": sorted(state.get("tool_results", {}).keys()),
        }
        data = {
            "document_id": state.get("document_id"),
            "document_title": state.get("document_title"),
            "tool_results": state.get("tool_results", {}),
        }
        if state.get("needs_clarification") and state.get("error") is None:
            return GraphResult.ok(
                response_text=state.get("response_text"),
                data=data,
                route=route,
                diagnostics=diagnostics,
                trace=state.get("trace", []),
                messages=state.get("history", []),
            )
        if state.get("error") is not None:
            error = state["error"]
            diagnostics["error"] = error.get("diagnostics", {})
            return GraphResult.fail(
                response_text=state.get("response_text"),
                error_code=error.get("error_code"),
                data=data,
                route=route,
                diagnostics=diagnostics,
                trace=state.get("trace", []),
                messages=state.get("history", []),
            )
        return GraphResult.ok(
            response_text=state.get("response_text"),
            data=data,
            route=route,
            diagnostics=diagnostics,
            trace=state.get("trace", []),
            messages=state.get("history", []),
        )

    @staticmethod
    def _merge_state(state: AgentState, patch: dict[str, Any]) -> AgentState:
        merged = dict(state)
        merged.update(patch)
        return merged  # type: ignore[return-value]

    def _next_node_name(self, current_node: str, state: AgentState) -> str:
        if current_node == "route_request":
            return self._entry_branch(state)
        if current_node == "find_document":
            return self._after_find_document_branch(state)
        if current_node in {
            "list_documents",
            "document_details",
            "explore_document",
            "retrieve_evidence",
            "answer_question",
            "run_quality_gate",
            "retrieval_trace",
        }:
            return self._post_action_branch(state)
        if current_node in {"clarify_request", "error_handler"}:
            return "final_response"
        if current_node == "final_response":
            return END
        return END

    @staticmethod
    def _entry_branch(state: AgentState) -> str:
        route = state.get("route")
        if route == RouteType.LIST_DOCUMENTS.value:
            return "list_documents"
        if route == RouteType.FIND_DOCUMENT.value:
            return "find_document" if _has_document_selector(state) else "clarify_request"
        if route == RouteType.DOCUMENT_DETAILS.value:
            return _document_branch_target(state, "document_details")
        if route == RouteType.DOCUMENT_EXPLORATION.value:
            return _document_branch_target(state, "explore_document")
        if route == RouteType.RETRIEVE_EVIDENCE.value:
            return _optional_document_branch_target(state, "retrieve_evidence")
        if route == RouteType.ANSWER_QUESTION.value:
            return _optional_document_branch_target(state, "answer_question")
        if route == RouteType.QUALITY_GATE.value:
            return "run_quality_gate"
        if route == RouteType.RETRIEVAL_TRACE.value:
            return _optional_document_branch_target(state, "retrieval_trace")
        return "clarify_request"

    @staticmethod
    def _after_find_document_branch(state: AgentState) -> str:
        if state.get("error") is not None:
            return "error_handler"
        if state.get("needs_clarification"):
            return "clarify_request"
        route = state.get("route")
        if route == RouteType.FIND_DOCUMENT.value:
            return "final_response"
        if route == RouteType.DOCUMENT_DETAILS.value:
            return "document_details"
        if route == RouteType.DOCUMENT_EXPLORATION.value:
            return "explore_document"
        if route == RouteType.RETRIEVE_EVIDENCE.value:
            return "retrieve_evidence"
        if route == RouteType.ANSWER_QUESTION.value:
            return "answer_question"
        if route == RouteType.RETRIEVAL_TRACE.value:
            return "retrieval_trace"
        return "final_response"

    @staticmethod
    def _post_action_branch(state: AgentState) -> str:
        if state.get("error") is not None:
            return "error_handler"
        if state.get("needs_clarification"):
            return "clarify_request"
        return "final_response"


def _has_document_selector(state: AgentState) -> bool:
    return bool(state.get("document_id") or state.get("document_query"))


def _document_branch_target(state: AgentState, target: str) -> str:
    if state.get("document_id"):
        return target
    if state.get("document_query"):
        return "find_document"
    return "clarify_request"


def _optional_document_branch_target(state: AgentState, target: str) -> str:
    if state.get("document_id"):
        return target
    if state.get("document_query"):
        return "find_document"
    return target

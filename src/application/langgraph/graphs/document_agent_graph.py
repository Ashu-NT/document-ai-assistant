from __future__ import annotations

from typing import Any

from src.application.langgraph.common import GraphMetadata, GraphResult, serialize_graph_value
from src.application.langgraph.factories.node_factory import NodeFactory
from src.application.langgraph.factories.tool_registry import ToolRegistry
from src.application.langgraph.memory import ConversationMemory
from src.application.langgraph.routing import IntentRouter, RouteType
from src.application.langgraph.state import AgentState, build_agent_state
from src.application.langgraph.validation import (
    GraphRequestValidator,
    GraphStateValidator,
)

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
        self._compiled_graph = self._compile_graph()

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
        llm_planning_enabled: bool = False,
        show_plan: bool = False,
        show_raw_plan: bool = False,
        top_k: int | None = None,
        conversation_id: str | None = None,
    ) -> GraphResult:
        initial_state = build_agent_state(
            user_input=user_input,
            document_id=document_id,
            document_query=document_query,
            allow_answer_generation=allow_answer_generation,
            include_context=include_context,
            llm_planning_enabled=llm_planning_enabled,
            show_plan=show_plan,
            show_raw_plan=show_raw_plan,
            top_k=top_k,
            conversation_id=conversation_id,
            session_id=session_id,
            history=[],
        )
        if self.memory is not None:
            session_snapshot = self.memory.load_session(initial_state["session_id"])
            initial_state["history"] = list(session_snapshot.get("history", []))
            initial_state["selected_document_id"] = session_snapshot.get(
                "selected_document_id"
            )
            initial_state["selected_document_title"] = session_snapshot.get(
                "selected_document_title"
            )
            initial_state["selected_document_file_name"] = session_snapshot.get(
                "selected_document_file_name"
            )
            initial_state["pending_clarification"] = session_snapshot.get(
                "pending_clarification"
            )
            initial_state["clarification_options"] = list(
                session_snapshot.get("clarification_options", [])
            )
            initial_state["clarification_question"] = session_snapshot.get(
                "clarification_question"
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

        final_state = self._invoke(initial_state)
        response_text = final_state.get("response_text")
        if self.memory is not None and response_text:
            self.memory.append_assistant_message(
                response_text,
                conversation_id=initial_state["session_id"],
            )
            final_state["history"] = self.memory.get_history()

        return self._build_result(final_state)

    def _build_nodes(self) -> dict[str, Any]:
        node_factory = NodeFactory()
        return node_factory.build_document_agent_nodes(
            tool_registry=self.tool_registry,
            intent_router=self.intent_router,
            memory=self.memory,
        )

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
                "blocked_action": "blocked_action",
                "create_plan": "create_plan",
                "list_documents": "list_documents",
                "find_document": "find_document",
                "document_details": "document_details",
                "explore_document": "explore_document",
                "retrieve_evidence": "retrieve_evidence",
                "answer_question": "answer_question",
                "run_quality_gate": "run_quality_gate",
                "retrieval_trace": "retrieval_trace",
                "session_command": "session_command",
                "clarify_request": "clarify_request",
            },
        )
        graph.add_conditional_edges(
            "create_plan",
            self._after_create_plan_branch,
            {
                "execute_plan": "execute_plan",
                "find_document": "find_document",
                "answer_question": "answer_question",
                "clarify_request": "clarify_request",
                "error_handler": "error_handler",
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
        graph.add_conditional_edges(
            "execute_plan",
            self._after_execute_plan_branch,
            {
                "plan_summary": "plan_summary",
                "clarify_request": "clarify_request",
                "error_handler": "error_handler",
            },
        )
        for action_node in (
            "blocked_action",
            "list_documents",
            "document_details",
            "explore_document",
            "retrieve_evidence",
            "answer_question",
            "run_quality_gate",
            "retrieval_trace",
            "session_command",
            "plan_summary",
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
        tool_results = state.get("tool_results", {})
        answer = _extract_answer(tool_results, state.get("response_text"))
        answer_intent = _extract_answer_intent(tool_results)
        citations = _extract_citations(tool_results)
        context_chunks = _extract_context_chunks(
            tool_results=tool_results,
            citations=citations,
            fallback_document_title=state.get("document_title")
            or state.get("selected_document_title"),
            selected_document_id=state.get("selected_document_id")
            or state.get("document_id"),
        )
        diagnostics = {
            "needs_clarification": state.get("needs_clarification", False),
            "configured_tools": sorted(tool_results.keys()),
            "plan_used": bool(state.get("execution_plan")),
            "plan_success": state.get("plan_success"),
            "planning_source": state.get("planning_source"),
            "unsafe_request_blocked": state.get("unsafe_request_blocked", False),
        }
        data = {
            "document_id": state.get("document_id"),
            "document_title": state.get("document_title"),
            "selected_document_id": state.get("selected_document_id"),
            "selected_document_title": state.get("selected_document_title"),
            "selected_document_file_name": state.get("selected_document_file_name"),
            "pending_clarification": state.get("pending_clarification"),
            "clarification_options": state.get("clarification_options", []),
            "clarification_question": state.get("clarification_question"),
            "should_exit": state.get("should_exit", False),
            "answer": answer,
            "answer_intent": answer_intent,
            "context_chunks": context_chunks,
            "citations": citations,
            "execution_plan": state.get("execution_plan"),
            "validated_plan": state.get("validated_plan"),
            "plan_steps": state.get("plan_steps", []),
            "plan_results": state.get("plan_results", {}),
            "plan_success": state.get("plan_success"),
            "failed_plan_step": state.get("failed_plan_step"),
            "planning_source": state.get("planning_source"),
            "planning_errors": state.get("planning_errors", []),
            "planning_warnings": state.get("planning_warnings", []),
            "raw_llm_plan": state.get("raw_llm_plan"),
            "unsafe_request_blocked": state.get("unsafe_request_blocked", False),
            "blocked_reason": state.get("blocked_reason"),
            "blocked_terms": state.get("blocked_terms", []),
            "tool_results": tool_results,
        }
        execution_plan = state.get("execution_plan")
        if isinstance(execution_plan, dict):
            diagnostics["plan_id"] = execution_plan.get("plan_id")
            diagnostics["plan_goal"] = execution_plan.get("goal")
        if state.get("planning_errors"):
            diagnostics["planning_errors"] = state.get("planning_errors", [])
        if state.get("planning_warnings"):
            diagnostics["planning_warnings"] = state.get("planning_warnings", [])
        if state.get("blocked_reason"):
            diagnostics["blocked_reason"] = state.get("blocked_reason")
        if state.get("blocked_terms"):
            diagnostics["blocked_terms"] = state.get("blocked_terms", [])
        if answer_intent is not None:
            diagnostics["answer_intent"] = answer_intent
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
        if current_node == "create_plan":
            return self._after_create_plan_branch(state)
        if current_node == "find_document":
            return self._after_find_document_branch(state)
        if current_node == "execute_plan":
            return self._after_execute_plan_branch(state)
        if current_node in {
            "blocked_action",
            "list_documents",
            "document_details",
            "explore_document",
            "retrieve_evidence",
            "answer_question",
            "run_quality_gate",
            "retrieval_trace",
            "session_command",
            "plan_summary",
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
        if route == RouteType.BLOCKED_ACTION.value:
            return "blocked_action"
        if route == RouteType.LIST_DOCUMENTS.value:
            return "list_documents"
        if route == RouteType.SELECT_DOCUMENT.value:
            return "find_document" if _has_document_selector(state) else "clarify_request"
        if route in {
            RouteType.CURRENT_DOCUMENT.value,
            RouteType.CLEAR_DOCUMENT.value,
            RouteType.HELP.value,
            RouteType.EXIT.value,
        }:
            return "session_command"
        if route == RouteType.CLARIFICATION_RESPONSE.value:
            return "clarify_request"
        if route == RouteType.FIND_DOCUMENT.value:
            return "find_document" if _has_document_selector(state) else "clarify_request"
        if route == RouteType.PLANNED_TASK.value:
            return "create_plan"
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
        if route == RouteType.SELECT_DOCUMENT.value:
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
    def _after_create_plan_branch(state: AgentState) -> str:
        if state.get("error") is not None:
            return "error_handler"
        if state.get("needs_clarification"):
            return "clarify_request"
        if state.get("execution_plan"):
            return "execute_plan"
        return _optional_document_branch_target(state, "answer_question")

    @staticmethod
    def _after_execute_plan_branch(state: AgentState) -> str:
        if state.get("error") is not None:
            return "error_handler"
        if state.get("needs_clarification"):
            return "clarify_request"
        return "plan_summary"

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
    if state.get("selected_document_id"):
        return target
    if state.get("document_query"):
        return "find_document"
    return "clarify_request"


def _optional_document_branch_target(state: AgentState, target: str) -> str:
    if state.get("document_id"):
        return target
    if state.get("selected_document_id"):
        return target
    if state.get("document_query"):
        return "find_document"
    return target


def _extract_answer(
    tool_results: dict[str, Any],
    response_text: str | None,
) -> str | None:
    format_combined_payload = tool_results.get("format_combined_answer")
    if (
        response_text
        and isinstance(format_combined_payload, dict)
        and format_combined_payload.get("success", False)
    ):
        return response_text
    answer_question_payload = _tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        return (
            answer_question_payload.get("answer_text")
            or answer_question_payload.get("safe_user_message")
            or response_text
        )
    return response_text


def _extract_citations(tool_results: dict[str, Any]) -> list[dict[str, Any]]:
    answer_question_payload = _tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        citations = answer_question_payload.get("citations")
        if isinstance(citations, list):
            return serialize_graph_value(citations)

    retrieve_evidence_payload = _tool_payload(tool_results, "retrieve_evidence")
    if isinstance(retrieve_evidence_payload, dict):
        citations = retrieve_evidence_payload.get("citations")
        if isinstance(citations, list):
            return serialize_graph_value(citations)

    return []


def _extract_answer_intent(tool_results: dict[str, Any]) -> str | None:
    answer_question_payload = _tool_payload(tool_results, "answer_question")
    if not isinstance(answer_question_payload, dict):
        return None
    answer_intent = answer_question_payload.get("answer_intent")
    if isinstance(answer_intent, str) and answer_intent:
        return answer_intent

    diagnostics = answer_question_payload.get("diagnostics")
    if isinstance(diagnostics, dict):
        value = diagnostics.get("answer_intent")
        if isinstance(value, str) and value:
            return value
    return None


def _extract_context_chunks(
    *,
    tool_results: dict[str, Any],
    citations: list[dict[str, Any]],
    fallback_document_title: str | None,
    selected_document_id: str | None,
) -> list[dict[str, Any]]:
    approved_chunk_ids: set[str] = set()
    rejected_chunk_ids: set[str] = set()

    answer_question_payload = _tool_payload(tool_results, "answer_question")
    if isinstance(answer_question_payload, dict):
        approved_chunk_ids = set(answer_question_payload.get("approved_chunk_ids", []))
        rejected_chunk_ids = set(answer_question_payload.get("rejected_chunk_ids", []))
        retrieval_workflow_result = answer_question_payload.get("retrieval_result")
        if isinstance(retrieval_workflow_result, dict):
            context_chunks = retrieval_workflow_result.get("context_chunks")
            if isinstance(context_chunks, list):
                return _enrich_context_chunks(
                    context_chunks,
                    citations=citations,
                    fallback_document_title=fallback_document_title,
                    selected_document_id=selected_document_id,
                    approved_chunk_ids=approved_chunk_ids,
                    rejected_chunk_ids=rejected_chunk_ids,
                )

    retrieve_evidence_payload = _tool_payload(tool_results, "retrieve_evidence")
    if isinstance(retrieve_evidence_payload, dict):
        context_chunks = retrieve_evidence_payload.get("context_chunks")
        if isinstance(context_chunks, list):
            return _enrich_context_chunks(
                context_chunks,
                citations=citations,
                fallback_document_title=fallback_document_title,
                selected_document_id=selected_document_id,
                approved_chunk_ids=approved_chunk_ids,
                rejected_chunk_ids=rejected_chunk_ids,
            )

    return []


def _enrich_context_chunks(
    context_chunks: list[dict[str, Any]],
    *,
    citations: list[dict[str, Any]],
    fallback_document_title: str | None,
    selected_document_id: str | None,
    approved_chunk_ids: set[str],
    rejected_chunk_ids: set[str],
) -> list[dict[str, Any]]:
    citation_by_chunk_id = {
        citation.get("chunk_id"): citation
        for citation in citations
        if isinstance(citation, dict) and citation.get("chunk_id")
    }

    enriched_chunks: list[dict[str, Any]] = []
    for chunk in context_chunks:
        if not isinstance(chunk, dict):
            continue

        enriched_chunk = dict(chunk)
        chunk_id = str(enriched_chunk.get("chunk_id") or "")
        citation = citation_by_chunk_id.get(chunk_id)
        embedded_citation = enriched_chunk.get("citation")
        if isinstance(embedded_citation, dict) and citation is None:
            citation = embedded_citation

        document_id = enriched_chunk.get("document_id")
        document_title = None
        section_title = None
        if isinstance(citation, dict):
            document_title = citation.get("document_name")
            section_title = citation.get("section_title")

        if document_title is None and selected_document_id and document_id == selected_document_id:
            document_title = fallback_document_title

        if section_title is None:
            section_path = enriched_chunk.get("section_path") or []
            if isinstance(section_path, list) and section_path:
                section_title = section_path[-1]

        enriched_chunk["document_title"] = document_title
        enriched_chunk["section_title"] = section_title
        enriched_chunk["approved"] = chunk_id in approved_chunk_ids if approved_chunk_ids else None
        enriched_chunk["rejected"] = chunk_id in rejected_chunk_ids if rejected_chunk_ids else None
        enriched_chunks.append(serialize_graph_value(enriched_chunk))

    return enriched_chunks


def _tool_payload(
    tool_results: dict[str, Any],
    tool_name: str,
) -> Any | None:
    tool_result = tool_results.get(tool_name)
    if not isinstance(tool_result, dict):
        return None
    if not tool_result.get("success", False):
        return None
    return tool_result.get("data")

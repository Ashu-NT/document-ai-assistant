from __future__ import annotations

from typing import Any

from src.application.langgraph.graphs.document_agent import document_agent_router as router
from src.application.langgraph.state import AgentState

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:  # pragma: no cover
    END = "__end__"
    START = "__start__"
    StateGraph = None


def compile_graph(nodes: dict[str, Any]) -> Any | None:
    if StateGraph is None:
        return None

    graph = StateGraph(AgentState)
    for node_name, node in nodes.items():
        graph.add_node(node_name, node)

    graph.add_edge(START, "route_request")
    graph.add_conditional_edges(
        "route_request",
        router.entry_branch,
        {
            "blocked_action": "blocked_action",
            "out_of_scope": "out_of_scope",
            "create_plan": "create_plan",
            "create_research_plan": "create_research_plan",
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
        router.after_create_plan_branch,
        {
            "execute_plan": "execute_plan",
            "find_document": "find_document",
            "answer_question": "answer_question",
            "clarify_request": "clarify_request",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "create_research_plan",
        router.after_create_research_plan_branch,
        {
            "execute_research": "execute_research",
            "answer_question": "answer_question",
            "clarify_request": "clarify_request",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "find_document",
        router.after_find_document_branch,
        {
            "document_details": "document_details",
            "explore_document": "explore_document",
            "retrieve_evidence": "retrieve_evidence",
            "answer_question": "answer_question",
            "create_research_plan": "create_research_plan",
            "final_response": "final_response",
            "clarify_request": "clarify_request",
            "error_handler": "error_handler",
            "retrieval_trace": "retrieval_trace",
        },
    )
    graph.add_conditional_edges(
        "execute_plan",
        router.after_execute_plan_branch,
        {
            "plan_summary": "plan_summary",
            "clarify_request": "clarify_request",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "execute_research",
        router.after_execute_research_branch,
        {
            "evaluate_research": "evaluate_research",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "evaluate_research",
        router.after_evaluate_research_branch,
        {
            "execute_research": "execute_research",
            "synthesize_research": "synthesize_research",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "synthesize_research",
        router.after_synthesize_research_branch,
        {
            "research_summary": "research_summary",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "research_summary",
        router.after_research_summary_branch,
        {
            "reflect_answer": "reflect_answer",
            "final_response": "final_response",
            "error_handler": "error_handler",
        },
    )
    for action_node in (
        "blocked_action",
        "list_documents",
        "document_details",
        "explore_document",
        "retrieve_evidence",
        "run_quality_gate",
        "retrieval_trace",
        "session_command",
        "plan_summary",
    ):
        graph.add_conditional_edges(
            action_node,
            router.post_action_branch,
            {
                "final_response": "final_response",
                "clarify_request": "clarify_request",
                "error_handler": "error_handler",
            },
        )

    graph.add_conditional_edges(
        "answer_question",
        router.after_answer_question_branch,
        {
            "reflect_answer": "reflect_answer",
            "final_response": "final_response",
            "clarify_request": "clarify_request",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "reflect_answer",
        router.after_reflect_answer_branch,
        {
            "retry_retrieval": "retry_retrieval",
            "clarify_request": "clarify_request",
            "final_response": "final_response",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "retry_retrieval",
        router.after_retry_retrieval_branch,
        {
            "reflect_answer": "reflect_answer",
            "final_response": "final_response",
            "error_handler": "error_handler",
        },
    )
    graph.add_conditional_edges(
        "clarify_request",
        router.after_clarify_request_branch,
        {
            "answer_question": "answer_question",
            "final_response": "final_response",
            "error_handler": "error_handler",
        },
    )
    graph.add_edge("error_handler", "final_response")
    graph.add_edge("final_response", END)
    return graph.compile()

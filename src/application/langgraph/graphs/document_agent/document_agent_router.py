from __future__ import annotations

from src.application.langgraph.routing import RouteType
from src.application.langgraph.state import AgentState

try:
    from langgraph.graph import END
except ImportError:  # pragma: no cover
    END = "__end__"


def entry_branch(state: AgentState) -> str:
    route = state.get("route")
    if route == RouteType.BLOCKED_ACTION.value:
        return "blocked_action"
    if route == RouteType.OUT_OF_SCOPE.value:
        return "out_of_scope"
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
    if route == RouteType.DEEP_RESEARCH.value:
        return _deep_research_branch_target(state)
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


def after_find_document_branch(state: AgentState) -> str:
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
    if route == RouteType.DEEP_RESEARCH.value:
        return "create_research_plan"
    if route == RouteType.RETRIEVAL_TRACE.value:
        return "retrieval_trace"
    return "final_response"


def after_create_plan_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarify_request"
    if state.get("execution_plan"):
        return "execute_plan"
    return _optional_document_branch_target(state, "answer_question")


def after_create_research_plan_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarify_request"
    if state.get("research_plan"):
        return "execute_research"
    if state.get("route") == RouteType.ANSWER_QUESTION.value:
        return _optional_document_branch_target(state, "answer_question")
    return "error_handler"


def after_execute_plan_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarify_request"
    return "plan_summary"


def after_execute_research_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    return "evaluate_research"


def after_evaluate_research_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("research_followup_pending"):
        return "execute_research"
    return "synthesize_research"


def after_synthesize_research_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    return "research_summary"


def after_research_summary_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if _should_run_reflection(state):
        return "reflect_answer"
    return "final_response"


def post_action_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarify_request"
    return "final_response"


def after_answer_question_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarify_request"
    if _should_run_reflection(state):
        return "reflect_answer"
    return "final_response"


def after_reflect_answer_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarify_request"
    decision = state.get("reflection_decision")
    if decision == "RETRIEVE_AGAIN":
        return "retry_retrieval"
    if decision == "CLARIFY":
        return "clarify_request"
    return "final_response"


def after_retry_retrieval_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "clarify_request"
    if state.get("reflection_decision") == "FAIL":
        return "final_response"
    if _should_run_reflection(state):
        return "reflect_answer"
    return "final_response"


def after_clarify_request_branch(state: AgentState) -> str:
    if state.get("error") is not None:
        return "error_handler"
    if state.get("needs_clarification"):
        return "final_response"
    if state.get("route") == RouteType.ANSWER_QUESTION.value and state.get("question"):
        return "answer_question"
    return "final_response"


def next_node_name(current_node: str, state: AgentState) -> str:
    if current_node == "route_request":
        return entry_branch(state)
    if current_node == "create_plan":
        return after_create_plan_branch(state)
    if current_node == "create_research_plan":
        return after_create_research_plan_branch(state)
    if current_node == "find_document":
        return after_find_document_branch(state)
    if current_node == "execute_plan":
        return after_execute_plan_branch(state)
    if current_node == "execute_research":
        return after_execute_research_branch(state)
    if current_node == "evaluate_research":
        return after_evaluate_research_branch(state)
    if current_node == "synthesize_research":
        return after_synthesize_research_branch(state)
    if current_node == "research_summary":
        return after_research_summary_branch(state)
    if current_node in {
        "blocked_action",
        "out_of_scope",
        "list_documents",
        "document_details",
        "explore_document",
        "retrieve_evidence",
        "run_quality_gate",
        "retrieval_trace",
        "session_command",
        "plan_summary",
    }:
        return post_action_branch(state)
    if current_node == "answer_question":
        return after_answer_question_branch(state)
    if current_node == "reflect_answer":
        return after_reflect_answer_branch(state)
    if current_node == "retry_retrieval":
        return after_retry_retrieval_branch(state)
    if current_node == "clarify_request":
        return after_clarify_request_branch(state)
    if current_node == "error_handler":
        return "final_response"
    if current_node == "final_response":
        return END
    return END


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


def _deep_research_branch_target(state: AgentState) -> str:
    if state.get("document_id"):
        return "create_research_plan"
    if state.get("selected_document_id"):
        return "create_research_plan"
    if state.get("document_query"):
        return "find_document"
    return "create_research_plan"


def _should_run_reflection(state: AgentState) -> bool:
    if not state.get("reflection_enabled", False):
        return False
    if state.get("route") != RouteType.ANSWER_QUESTION.value:
        return False
    if not state.get("allow_answer_generation", False):
        return False
    return int(state.get("reflection_attempts", 0)) <= 1

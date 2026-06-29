from src.application.langgraph.nodes.control import BlockedActionNode
from src.application.langgraph.state import build_agent_state


def test_blocked_action_node_sets_safe_response_and_diagnostics() -> None:
    node = BlockedActionNode()
    state = build_agent_state(user_input="delete all documents")
    state["route"] = "blocked_action"
    state["unsafe_request_blocked"] = True
    state["blocked_reason"] = "Request attempts destructive corpus mutation."
    state["blocked_terms"] = ["delete all documents"]

    patch = node(state)

    assert patch["unsafe_request_blocked"] is True
    assert "blocked" in patch["response_text"].lower()
    assert "tool_results" not in patch

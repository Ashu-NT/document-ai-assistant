from src.application.langgraph.nodes.control.clarify_request_node import (
    ClarifyRequestNode,
)
from src.application.langgraph.routing import RouteType


def test_reflection_clarification_response_resumes_answer_question_route() -> None:
    node = ClarifyRequestNode()

    patch = node(
        {
            "trace": [],
            "route": RouteType.CLARIFICATION_RESPONSE.value,
            "user_input": "2",
            "question": "What are the maintenance tasks?",
            "pending_clarification": {
                "kind": "reflection_clarification",
                "resume_route": RouteType.ANSWER_QUESTION.value,
                "original_user_input": "What are the maintenance tasks?",
            },
            "clarification_options": [
                {"label": "maintenance tasks", "value": "maintenance tasks"},
                {"label": "maintenance intervals", "value": "maintenance intervals"},
            ],
            "clarification_question": "Do you want maintenance tasks or maintenance intervals?",
            "clarification_message": "Do you want maintenance tasks or maintenance intervals?",
            "clarification_candidate_index": 1,
        }
    )

    assert patch["route"] == RouteType.ANSWER_QUESTION.value
    assert patch["needs_clarification"] is False
    assert patch["pending_clarification"] is None
    assert "maintenance intervals" in patch["question"]

from src.application.langgraph.nodes.control import FinalResponseNode
from src.application.langgraph.reflection.constants import (
    REFLECTION_SAFE_FAILURE_MESSAGE,
)


class _FakePostResponseGuardrailService:
    def __init__(self, safe_response_text: str, *, allowed: bool = True) -> None:
        self.safe_response_text = safe_response_text
        self.allowed = allowed

    def check(self, context):
        return (
            type(
                "GuardrailResult",
                (),
                {
                    "decision": type(
                        "Decision", (), {"value": "allow" if self.allowed else "safe_fallback"}
                    )(),
                    "allowed": self.allowed,
                    "trace_id": "trace_1",
                    "diagnostics": {"guardrail_trace": []},
                    "to_dict": lambda self: {
                        "decision": "allow" if self.allowed else "safe_fallback",
                        "allowed": self.allowed,
                    },
                },
            )(),
            self.safe_response_text,
        )


def test_final_response_node_prefers_safe_fallback_response_text() -> None:
    node = FinalResponseNode()

    patch = node(
        {
            "route": "deep_research",
            "response_text": "Fallback response",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Preferred answer",
                    },
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert patch["response_text"] == "Fallback response"


def test_final_response_node_uses_answer_payload_when_fallback_missing() -> None:
    node = FinalResponseNode()

    patch = node(
        {
            "route": "deep_research",
            "response_text": None,
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Preferred answer",
                    },
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert patch["response_text"] == "Preferred answer"


def test_final_response_node_accept_with_limitations_recovers_generated_answer_from_safe_failure() -> None:
    node = FinalResponseNode(
        post_response_guardrail_service=_FakePostResponseGuardrailService(
            "I could not verify a grounded answer confidently enough from the current document evidence."
        )
    )

    patch = node(
        {
            "route": "answer_question",
            "response_text": "Generated grounded answer.",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Generated grounded answer.",
                        "citations": [{"chunk_id": "chunk_1"}],
                        "retrieval_result": {"context_chunks": [{"chunk_id": "chunk_1"}]},
                    },
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert patch["response_text"] == "Generated grounded answer."
    assert "Recovered generated answer" in patch["final_response_warning"]


def test_final_response_node_accept_recovers_generated_answer_from_safe_failure() -> None:
    node = FinalResponseNode(
        post_response_guardrail_service=_FakePostResponseGuardrailService(
            "I could not verify a grounded answer confidently enough from the current document evidence."
        )
    )

    patch = node(
        {
            "route": "answer_question",
            "response_text": "The serial number is listed on p.50 and p.72.",
            "reflection_decision": "ACCEPT",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "The serial number is listed on p.50 and p.72.",
                        "citations": [{"chunk_id": "chunk_50"}],
                        "retrieval_result": {"context_chunks": [{"chunk_id": "chunk_50"}]},
                    },
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert patch["response_text"] == "The serial number is listed on p.50 and p.72."
    assert "Recovered generated answer" in patch["final_response_warning"]


def test_final_response_node_does_not_recover_answer_when_guardrail_replaced_text() -> None:
    """Finding 5.5: when the guardrail itself replaced response_text with a
    safe-fallback message (allowed=False), the recovery heuristic must not
    swap the raw generated answer back in, even though the current text
    string-matches the same sentinel message reflection could have
    legitimately produced on its own."""
    node = FinalResponseNode(
        post_response_guardrail_service=_FakePostResponseGuardrailService(
            "I could not verify a grounded answer confidently enough from the current document evidence.",
            allowed=False,
        )
    )

    patch = node(
        {
            "route": "answer_question",
            "response_text": "Generated grounded answer.",
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Generated grounded answer.",
                        "citations": [{"chunk_id": "chunk_1"}],
                        "retrieval_result": {"context_chunks": [{"chunk_id": "chunk_1"}]},
                    },
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert patch["response_text"] == (
        "I could not verify a grounded answer confidently enough from the current document evidence."
    )
    assert patch["response_text_guardrail_replaced"] is True
    assert patch["final_response_warning"] is None


def test_final_response_node_marks_guardrail_replaced_false_on_normal_allow() -> None:
    node = FinalResponseNode(
        post_response_guardrail_service=_FakePostResponseGuardrailService(
            "Fallback response",
            allowed=True,
        )
    )

    patch = node(
        {
            "route": "deep_research",
            "response_text": "Fallback response",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {"answer_text": "Preferred answer"},
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert patch["response_text_guardrail_replaced"] is False


def test_final_response_node_fail_keeps_safe_failure_message() -> None:
    node = FinalResponseNode(
        post_response_guardrail_service=_FakePostResponseGuardrailService(
            REFLECTION_SAFE_FAILURE_MESSAGE
        )
    )

    patch = node(
        {
            "route": "answer_question",
            "response_text": REFLECTION_SAFE_FAILURE_MESSAGE,
            "reflection_decision": "FAIL",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Old generated answer.",
                    },
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert patch["response_text"] == REFLECTION_SAFE_FAILURE_MESSAGE

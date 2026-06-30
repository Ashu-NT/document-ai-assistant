from src.application.langgraph.nodes.control import FinalResponseNode


def test_final_response_node_prefers_answer_payload_text() -> None:
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

    assert patch["response_text"] == "Preferred answer"

import pytest

from src.application.langgraph import DocumentAgentGraph, ToolRegistry


@pytest.mark.parametrize(
    ("reflection_decision", "answer_text"),
    [
        (
            "ACCEPT_WITH_LIMITATIONS",
            "Daily, weekly, monthly, and annual maintenance intervals are listed on pp.58-59.",
        ),
        (
            "ACCEPT",
            "The part and serial number details are listed on p.50 and p.72.",
        ),
    ],
)
def test_build_result_preserves_generated_answer_for_usable_reflection_decisions(
    reflection_decision: str,
    answer_text: str,
) -> None:
    graph = DocumentAgentGraph(ToolRegistry())

    result = graph._build_result(  # noqa: SLF001
        {
            "route": "answer_question",
            "response_text": (
                "I could not verify a grounded answer confidently enough from the "
                "current document evidence."
            ),
            "reflection_decision": reflection_decision,
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": answer_text,
                        "citations": [{"chunk_id": "chunk_58"}],
                        "retrieval_result": {"context_chunks": []},
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.response_text == answer_text
    assert result.data["answer"] == result.response_text

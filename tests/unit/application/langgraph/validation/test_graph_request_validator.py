from src.application.langgraph.validation import GraphRequestValidator


def test_graph_request_validator_rejects_empty_input() -> None:
    result = GraphRequestValidator().validate(
        {
            "user_input": "   ",
            "document_id": None,
            "top_k": None,
            "allow_answer_generation": False,
            "include_context": False,
        }
    )

    assert result.is_valid is False
    assert result.issues[0].field == "user_input"

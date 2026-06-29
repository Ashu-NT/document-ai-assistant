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


def test_graph_request_validator_rejects_unsafe_session_id() -> None:
    result = GraphRequestValidator().validate(
        {
            "user_input": "open FWC12",
            "document_id": None,
            "top_k": None,
            "allow_answer_generation": False,
            "include_context": False,
            "session_id": "../bad",
        }
    )

    assert result.is_valid is False
    assert result.issues[0].field == "session_id"

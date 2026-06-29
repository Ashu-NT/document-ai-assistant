from src.application.langgraph.validation import GraphStateValidator


def test_graph_state_validator_rejects_selected_title_without_selected_id() -> None:
    result = GraphStateValidator().validate(
        {
            "selected_document_id": None,
            "selected_document_title": "FWC12",
            "selected_document_file_name": None,
            "pending_clarification": None,
            "clarification_options": [],
            "clarification_question": None,
            "clarification_candidate_index": None,
        }
    )

    assert result.is_valid is False
    assert result.issues[0].field == "selected_document_id"


def test_graph_state_validator_rejects_out_of_range_candidate_index() -> None:
    result = GraphStateValidator().validate(
        {
            "selected_document_id": None,
            "selected_document_title": None,
            "selected_document_file_name": None,
            "pending_clarification": {"kind": "document_selection"},
            "clarification_options": [{"document_id": "doc-1"}],
            "clarification_question": "Which document?",
            "clarification_candidate_index": 3,
        }
    )

    assert result.is_valid is False
    assert result.issues[0].field == "clarification_candidate_index"

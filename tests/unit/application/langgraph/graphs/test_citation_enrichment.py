from src.application.langgraph.graphs.document_agent.document_agent_result_builder import (
    build_result,
)


def test_build_result_fills_missing_selected_document_name_in_citations() -> None:
    result = build_result(
        {
            "route": "answer_question",
            "response_text": "Grounded answer.",
            "selected_document_id": "doc_001",
            "selected_document_title": "FWC12 Manual",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Grounded answer.",
                        "citations": [
                            {
                                "chunk_id": "chunk_001",
                                "document_id": "doc_001",
                                "section_title": "Maintenance Schedule",
                            }
                        ],
                        "retrieval_result": {"context_chunks": []},
                    },
                }
            },
            "trace": [],
            "error": None,
        }
    )

    assert result.data["citations"][0]["document_name"] == "FWC12 Manual"

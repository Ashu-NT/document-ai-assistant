from src.application.langgraph.graphs.document_agent.document_agent_result_builder import (
    build_result,
)


def test_build_result_surfaces_deterministic_render_provenance() -> None:
    result = build_result(
        {
            "route": "answer_question",
            "response_text": "Answer.",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Answer.",
                        "diagnostics": {
                            "model_name": "deterministic_maintenance_schedule_renderer"
                        },
                        "citations": [],
                        "retrieval_result": {"context_chunks": []},
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.data["render_provenance"] == "parsed maintenance schedule data"
    assert result.diagnostics["render_provenance"] == "parsed maintenance schedule data"


def test_build_result_surfaces_llm_render_provenance_label() -> None:
    result = build_result(
        {
            "route": "answer_question",
            "response_text": "Answer.",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Answer.",
                        "diagnostics": {"model_name": "qwen3:8b"},
                        "citations": [],
                        "retrieval_result": {"context_chunks": []},
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.data["render_provenance"] == "AI-generated summary"

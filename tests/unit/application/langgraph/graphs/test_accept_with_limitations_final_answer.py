import pytest

from src.application.langgraph.graphs.document_agent.document_agent_result_builder import (
    build_result,
)


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
    result = build_result(
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


def test_build_result_does_not_recover_answer_when_guardrail_replaced_text() -> None:
    """Finding 5.5: when final_response_node marked response_text as having
    been replaced by the post-response guardrail (response_text_guardrail_
    replaced=True), build_result must not swap the raw generated answer
    back in even though it otherwise looks like a legitimate reflection
    recovery case."""
    safe_failure_message = (
        "I could not verify a grounded answer confidently enough from the "
        "current document evidence."
    )
    result = build_result(
        {
            "route": "answer_question",
            "response_text": safe_failure_message,
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
            "response_text_guardrail_replaced": True,
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Daily, weekly, monthly, and annual maintenance intervals are listed on pp.58-59.",
                        "citations": [{"chunk_id": "chunk_58"}],
                        "retrieval_result": {"context_chunks": []},
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.response_text == safe_failure_message
    assert result.data["response_text_guardrail_replaced"] is True


def test_build_result_still_recovers_answer_when_guardrail_did_not_replace_text() -> None:
    """Confirms the fix in the test above did not change existing behavior
    when the marker is absent (the normal, non-guardrail-replaced case)."""
    safe_failure_message = (
        "I could not verify a grounded answer confidently enough from the "
        "current document evidence."
    )
    answer_text = "Daily, weekly, monthly, and annual maintenance intervals are listed on pp.58-59."
    result = build_result(
        {
            "route": "answer_question",
            "response_text": safe_failure_message,
            "reflection_decision": "ACCEPT_WITH_LIMITATIONS",
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
    assert result.data["response_text_guardrail_replaced"] is False


def test_build_result_surfaces_limitation_note_sections_and_reference_notes() -> None:
    """CLI/LangGraph rendering follow-up: these three fields must survive
    from the answer_question tool payload into GraphResult.data -- they
    were previously dropped here even though AnswerGenerationService/
    QuestionAnsweringResult already compute them."""
    result = build_result(
        {
            "route": "answer_question",
            "response_text": "The filter is replaced every 1000 hours.",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "The filter is replaced every 1000 hours.",
                        "citations": [],
                        "retrieval_result": {"context_chunks": []},
                        "limitation_note": "Only the primary interval was found.",
                        "sections": [
                            {
                                "heading": "Maintenance interval",
                                "body": "Replace every 1000 hours.",
                                "reference_note_ids": ["r1"],
                            }
                        ],
                        "reference_notes": [
                            {
                                "note_id": "r1",
                                "claim_text": "Replace every 1000 operating hours.",
                                "source_number": 1,
                                "chunk_id": "chunk_001",
                            }
                        ],
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.data["limitation_note"] == "Only the primary interval was found."
    assert result.data["sections"] == [
        {
            "heading": "Maintenance interval",
            "body": "Replace every 1000 hours.",
            "reference_note_ids": ["r1"],
        }
    ]
    assert result.data["reference_notes"] == [
        {
            "note_id": "r1",
            "claim_text": "Replace every 1000 operating hours.",
            "source_number": 1,
            "chunk_id": "chunk_001",
        }
    ]


def test_build_result_surfaces_post_answer_guardrail_warnings() -> None:
    """Finding 5.1: post_answer_guardrail_warnings is computed by the answer
    generation pipeline and placed on QuestionAnsweringResult.diagnostics,
    but was previously dropped here -- confirmed reachable at
    tool_results["answer_question"]["data"]["diagnostics"]
    ["post_answer_guardrail_warnings"]."""
    result = build_result(
        {
            "route": "answer_question",
            "response_text": "The filter is replaced every 1000 hours.",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "The filter is replaced every 1000 hours.",
                        "citations": [],
                        "retrieval_result": {"context_chunks": []},
                        "diagnostics": {
                            "post_answer_guardrail_warnings": [
                                {
                                    "decision": "unsupported_claims",
                                    "reason": "1 section(s) have no supporting reference notes.",
                                    "violations": [
                                        "Section 'Overview' has no reference notes supporting its content."
                                    ],
                                }
                            ]
                        },
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.data["post_answer_guardrail_warnings"] == [
        {
            "decision": "unsupported_claims",
            "reason": "1 section(s) have no supporting reference notes.",
            "violations": [
                "Section 'Overview' has no reference notes supporting its content."
            ],
        }
    ]


def test_build_result_defaults_post_answer_guardrail_warnings_when_absent() -> None:
    result = build_result(
        {
            "route": "answer_question",
            "response_text": "Answer.",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Answer.",
                        "citations": [],
                        "retrieval_result": {"context_chunks": []},
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.data["post_answer_guardrail_warnings"] == []


def test_build_result_defaults_limitation_note_sections_and_reference_notes_when_absent() -> None:
    result = build_result(
        {
            "route": "answer_question",
            "response_text": "Answer.",
            "tool_results": {
                "answer_question": {
                    "success": True,
                    "data": {
                        "answer_text": "Answer.",
                        "citations": [],
                        "retrieval_result": {"context_chunks": []},
                    },
                }
            },
            "trace": [],
            "history": [],
        }
    )

    assert result.data["limitation_note"] is None
    assert result.data["sections"] == []
    assert result.data["reference_notes"] == []

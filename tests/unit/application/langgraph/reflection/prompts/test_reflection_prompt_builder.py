from src.application.langgraph.reflection.prompts import ReflectionPromptBuilder


def test_reflection_prompt_builder_includes_required_review_inputs() -> None:
    builder = ReflectionPromptBuilder()

    prompt = builder.build(
        original_user_question="What are the maintenance intervals?",
        selected_document_id="doc_123",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        generated_answer="The maintenance interval is 500 hours.",
        approved_chunk_summaries=[
            {
                "chunk_id": "chunk_1",
                "chunk_type": "maintenance_interval",
                "section_path": ["Maintenance", "Schedule"],
                "source": {"page_start": 12},
                "score": 0.91,
                "content": "Oil change interval is 500 hours.",
            }
        ],
        rejected_chunk_summaries=[],
        citations=[],
        context_document_ids=["doc_123"],
        reflection_attempt_count=0,
        retry_count=0,
    )

    assert "What are the maintenance intervals?" in prompt
    assert "You are reviewing a document-grounded answer." in prompt
    assert "Return JSON only." in prompt
    assert (
        '"decision": "ACCEPT | ACCEPT_WITH_LIMITATIONS | RETRIEVE_AGAIN | CLARIFY | FAIL"'
        in prompt
    )


def test_reflection_prompt_builder_adds_maintenance_interval_rules_and_hides_context_ids() -> None:
    builder = ReflectionPromptBuilder()

    prompt = builder.build(
        original_user_question="What are the maintenance intervals?",
        selected_document_id="doc_123",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        generated_answer="Weekly maintenance on page 58.",
        approved_chunk_summaries=[],
        rejected_chunk_summaries=[],
        citations=[],
        context_document_ids=["doc_123", "doc_456"],
        reflection_attempt_count=0,
        retry_count=0,
    )

    assert "Maintenance interval review rules:" in prompt
    assert "ACCEPT_WITH_LIMITATIONS if the answer is grounded but may be incomplete." in prompt
    assert (
        "Reject the answer if it mainly contains unrelated specifications"
        in prompt
    )
    assert "Context document ids: -" in prompt
    assert "doc_456" not in prompt

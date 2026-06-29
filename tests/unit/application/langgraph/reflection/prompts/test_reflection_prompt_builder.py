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
    assert '"decision": "ACCEPT | RETRIEVE_AGAIN | CLARIFY | FAIL"' in prompt

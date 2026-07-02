from src.application.langgraph.reflection.models import ReflectionDecisionType
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.services import ReflectionService


def test_reflection_service_accepts_grounded_answer_without_llm() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="The maintenance interval is 500 hours on page 12.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "content": "Maintenance interval is 500 hours.",
                "source": {"page_start": 12},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_1", "source": {"page_start": 12}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT
    assert result.accepted is True


def test_reflection_service_requests_retry_when_evidence_is_missing() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert result.requires_retry is True


def test_reflection_service_rejects_maintenance_interval_answer_with_unrelated_specs() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer=(
            "The maintenance interval is weekly on page 58. Voltage: 400 V. "
            "Installed power: 5.5 kW."
        ),
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_58", "source": {"page_start": 58}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert "technical specifications" in result.decision.reason.lower()
    assert result.decision.retry_query is not None


def test_reflection_service_rejects_maintenance_interval_answer_without_references() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="The maintenance interval is weekly.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert "grounded references" in result.decision.reason.lower()

from src.application.langgraph.reflection.models import ReflectionDecisionType
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.services import ReflectionService


class _FakeLLMService:
    def __init__(self, response: str) -> None:
        self.response = response

    def generate(self, prompt: str, model: str | None = None) -> str:
        return self.response


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

    assert result.decision.decision == ReflectionDecisionType.FAIL
    assert result.failed is True


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

    assert result.decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert "grounded references" in result.decision.reason.lower()
    assert result.accepted is True


def test_reflection_service_downgrades_clarify_without_question_to_accept_with_limitations() -> None:
    service = ReflectionService(
        llm_service=_FakeLLMService(
            '{"decision":"CLARIFY","confidence":0.61,"reason":"Need clarification.","retry_query":null,"clarification_question":null,"missing_information":["annual interval"]}'
        ),
        policy=ReflectionPolicy(enabled=True),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="Weekly maintenance latest after 100 operating hours (page 58).",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_58", "source": {"page_start": 58}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.requires_clarification is False
    assert result.failed is False


def test_reflection_service_retry_limit_with_evidence_returns_accept_with_limitations() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False, max_retrieval_retries=1),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="Weekly maintenance latest after 100 operating hours.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_58",
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        citations=[],
        reflection_attempts=0,
        retrieval_retry_count=1,
    )

    assert result.decision.decision == ReflectionDecisionType.ACCEPT_WITH_LIMITATIONS
    assert result.accepted is True


def test_reflection_service_spec_only_evidence_stays_retry_or_fail() -> None:
    service = ReflectionService(
        policy=ReflectionPolicy(enabled=False),
    )

    result = service.review(
        original_user_question="What are the maintenance intervals?",
        generated_answer="The pump voltage is 400 V and the installed power is 5.5 kW.",
        selected_document_id="doc_1",
        selected_document_title="FWC12 Manual",
        answer_intent="maintenance_summary",
        approved_chunks=[
            {
                "chunk_id": "chunk_spec",
                "document_id": "doc_1",
                "chunk_type": "technical_specification",
                "content": "Voltage 400 V. Installed power 5.5 kW.",
                "source": {"page_start": 50},
            }
        ],
        rejected_chunks=[],
        citations=[{"chunk_id": "chunk_spec", "source": {"page_start": 50}}],
        reflection_attempts=0,
        retrieval_retry_count=0,
    )

    assert result.decision.decision in {
        ReflectionDecisionType.RETRIEVE_AGAIN,
        ReflectionDecisionType.FAIL,
    }

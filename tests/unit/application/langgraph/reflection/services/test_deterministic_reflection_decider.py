from src.application.langgraph.reflection.evaluators.answer_quality_scorer import (
    AnswerQualityScorer,
)
from src.application.langgraph.reflection.evaluators.evidence_quality_scorer import (
    EvidenceQualityScorer,
)
from src.application.langgraph.reflection.models import ReflectionDecisionType
from src.application.langgraph.reflection.policies import ReflectionPolicy
from src.application.langgraph.reflection.services.deterministic_reflection_decider import (
    DeterministicReflectionDecider,
)

_QUESTION = "What is the pump seal replacement procedure?"


def test_insufficient_evidence_retry_query_is_identical_to_original_question() -> None:
    """Reproduces finding 4.5: the insufficient-evidence RETRIEVE_AGAIN
    branch previously set no retry_query at all, letting RetryQueryBuilder's
    fallback append non-search-term boilerplate ("additional grounded
    evidence") to the query text. It must now carry the original question
    verbatim as its retry_query."""
    answer_quality = AnswerQualityScorer.score(
        question=_QUESTION, answer="No answer.", citations=[]
    )
    evidence_quality = EvidenceQualityScorer.score(
        approved_chunks=[], rejected_chunks=[], selected_document_id="doc_1"
    )

    decision = DeterministicReflectionDecider.decide(
        policy=ReflectionPolicy(),
        answer_quality=answer_quality,
        evidence_quality=evidence_quality,
        question=_QUESTION,
        answer="No answer.",
        answer_intent="procedure",
        citations=[],
        selected_document_id="doc_1",
        approved_chunks=[],
        retrieval_retry_count=0,
    )

    assert decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert decision.retry_query == _QUESTION
    # missing_information stays as a human-readable diagnostic -- unchanged.
    assert decision.missing_information == ["additional grounded evidence"]


def test_generic_incompleteness_retry_query_is_identical_to_original_question() -> None:
    """Same rationale, for the final generic RETRIEVE_AGAIN fallback branch."""
    answer_quality = AnswerQualityScorer.score(
        question=_QUESTION,
        answer="Some incomplete answer with weak signals.",
        citations=[],
    )
    evidence_quality = EvidenceQualityScorer.score(
        approved_chunks=[
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "content": "Some unrelated content.",
                "source": {"page_start": 1},
            }
        ],
        rejected_chunks=[],
        selected_document_id="doc_1",
    )

    decision = DeterministicReflectionDecider.decide(
        policy=ReflectionPolicy(
            minimum_answer_quality_score=0.99,
            minimum_evidence_quality_score=0.99,
        ),
        answer_quality=answer_quality,
        evidence_quality=evidence_quality,
        question=_QUESTION,
        answer="Some incomplete answer with weak signals.",
        answer_intent="procedure",
        citations=[],
        selected_document_id="doc_1",
        approved_chunks=[
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "content": "Some unrelated content.",
                "source": {"page_start": 1},
            }
        ],
        retrieval_retry_count=0,
    )

    assert decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert decision.retry_query == _QUESTION
    assert decision.missing_information == ["more specific supporting evidence"]


def test_maintenance_unrelated_specs_branch_still_sets_its_real_reformulation_query() -> None:
    """Confirms a branch that already has a real, specific reformulation
    signal is untouched by this fix."""
    question = "What are the maintenance intervals?"
    answer = "The maintenance interval is weekly. Voltage: 400 V."
    answer_quality = AnswerQualityScorer.score(question=question, answer=answer, citations=[])
    evidence_quality = EvidenceQualityScorer.score(
        approved_chunks=[
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        rejected_chunks=[],
        selected_document_id="doc_1",
    )

    decision = DeterministicReflectionDecider.decide(
        policy=ReflectionPolicy(max_retrieval_retries=1),
        answer_quality=answer_quality,
        evidence_quality=evidence_quality,
        question=question,
        answer=answer,
        answer_intent="maintenance_summary",
        citations=[{"chunk_id": "chunk_1"}],
        selected_document_id="doc_1",
        approved_chunks=[
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "chunk_type": "maintenance_interval",
                "content": "Weekly maintenance latest after 100 operating hours.",
                "source": {"page_start": 58},
            }
        ],
        retrieval_retry_count=0,
    )

    assert decision.decision == ReflectionDecisionType.RETRIEVE_AGAIN
    assert decision.retry_query == (
        "maintenance intervals preventive maintenance schedule operating hours only"
    )

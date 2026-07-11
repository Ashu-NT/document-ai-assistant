from src.application.langgraph.reflection.models import ReflectionDecision, ReflectionDecisionType
from src.application.langgraph.reflection.services.retry_query_builder import RetryQueryBuilder

_QUESTION = "What is the pump seal replacement procedure?"


def test_retry_plan_query_is_identical_to_question_for_generic_decider_branches() -> None:
    """End-to-end proof for finding 4.5: when DeterministicReflectionDecider
    hands back a decision whose retry_query is the original question itself
    (the fix for the two generic branches), RetryQueryBuilder must use it
    verbatim -- not divert into _fallback_query()'s boilerplate-appending
    path."""
    builder = RetryQueryBuilder()
    decision = ReflectionDecision(
        decision=ReflectionDecisionType.RETRIEVE_AGAIN,
        confidence=0.9,
        reason="The answer did not have enough approved evidence.",
        retry_query=_QUESTION,
        missing_information=["additional grounded evidence"],
    )

    plan = builder.build(
        original_user_question=_QUESTION,
        answer_intent=None,
        selected_document_id="doc_1",
        reflection_decision=decision,
        top_k=10,
    )

    assert plan.retry_query == _QUESTION
    assert "additional grounded evidence" not in plan.retry_query


def test_fallback_query_is_still_used_when_decision_has_no_retry_query_at_all() -> None:
    """A decision that genuinely has no retry_query (e.g. built directly, not
    through the fixed decider branches) still falls back as before -- this
    fix is scoped to the two decider branches, not a rewrite of
    RetryQueryBuilder itself."""
    builder = RetryQueryBuilder()
    decision = ReflectionDecision(
        decision=ReflectionDecisionType.RETRIEVE_AGAIN,
        confidence=0.9,
        reason="Some other reason.",
        retry_query=None,
        missing_information=["some diagnostic detail"],
    )

    plan = builder.build(
        original_user_question=_QUESTION,
        answer_intent=None,
        selected_document_id="doc_1",
        reflection_decision=decision,
        top_k=10,
    )

    assert "some diagnostic detail" in plan.retry_query


def test_real_specific_reformulation_query_is_still_used_unchanged() -> None:
    builder = RetryQueryBuilder()
    decision = ReflectionDecision(
        decision=ReflectionDecisionType.RETRIEVE_AGAIN,
        confidence=0.9,
        reason="The answer mixed maintenance intervals with unrelated technical specifications.",
        retry_query=(
            "maintenance intervals preventive maintenance schedule operating hours only"
        ),
        missing_information=["maintenance interval evidence only"],
    )

    plan = builder.build(
        original_user_question="What are the maintenance intervals?",
        answer_intent="maintenance_summary",
        selected_document_id="doc_1",
        reflection_decision=decision,
        top_k=10,
    )

    assert plan.retry_query == (
        "maintenance intervals preventive maintenance schedule operating hours only"
    )

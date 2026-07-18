from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.strategies.retry_reformulation import (
    KeywordExpansionRetryReformulationStrategy,
    RetryReformulationContext,
)
from src.application.langgraph.retrieval_strategy import RetrievalStrategy

_QUESTION = "What is the pump seal replacement procedure?"


def _context(**overrides) -> RetryReformulationContext:
    defaults = dict(
        original_user_question=_QUESTION,
        answer_intent=None,
        selected_document_id="doc_1",
        reflection_decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.9,
            reason="The answer did not have enough approved evidence.",
        ),
        top_k=10,
    )
    defaults.update(overrides)
    return RetryReformulationContext(**defaults)


def test_uses_a_real_related_retry_query_verbatim() -> None:
    strategy = KeywordExpansionRetryReformulationStrategy()
    context = _context(
        reflection_decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.9,
            reason="Missing evidence.",
            retry_query=_QUESTION,
            missing_information=["additional grounded evidence"],
        )
    )

    plan = strategy.build_retry_plan(context)

    assert plan.retry_query == _QUESTION
    assert "additional grounded evidence" not in plan.retry_query


def test_falls_back_to_question_plus_missing_information_with_no_expansions() -> None:
    strategy = KeywordExpansionRetryReformulationStrategy()
    context = _context(
        reflection_decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.9,
            reason="Some other reason.",
            retry_query=None,
            missing_information=["some diagnostic detail"],
        )
    )

    plan = strategy.build_retry_plan(context)

    assert "some diagnostic detail" in plan.retry_query
    assert _QUESTION in plan.retry_query


def test_fallback_appends_configured_expansion_terms() -> None:
    # Word-level dedup (inherited unchanged from the retired
    # RetryQueryBuilder._fallback_query) means an expansion word already
    # present in the question is folded away -- use non-overlapping terms
    # so the assertion isn't testing that incidental behavior.
    strategy = KeywordExpansionRetryReformulationStrategy(
        expansion_terms=("lubrication", "lubricant")
    )
    context = _context(
        original_user_question="What are the maintenance intervals?",
        reflection_decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.9,
            reason="Missing interval evidence.",
            retry_query=None,
            missing_information=[],
        ),
    )

    plan = strategy.build_retry_plan(context)

    assert "lubrication" in plan.retry_query
    assert "lubricant" in plan.retry_query


def test_unrelated_retry_query_is_replaced_by_the_fallback() -> None:
    strategy = KeywordExpansionRetryReformulationStrategy()
    context = _context(
        reflection_decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.9,
            reason="Missing evidence.",
            retry_query="completely unrelated words about something else",
            missing_information=["specific missing fact"],
        )
    )

    plan = strategy.build_retry_plan(context)

    assert plan.retry_query != "completely unrelated words about something else"
    assert "specific missing fact" in plan.retry_query


def test_produces_a_retrieval_strategy_hint() -> None:
    strategy = KeywordExpansionRetryReformulationStrategy()
    context = _context(
        reflection_decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.9,
            reason="Need more maintenance interval evidence.",
            retry_query=None,
            missing_information=[],
        )
    )

    plan = strategy.build_retry_plan(context)

    assert plan.retrieval_strategy_hint == RetrievalStrategy.MAINTENANCE_LOOKUP
    assert RetrievalStrategy.TABLE_LOOKUP in plan.secondary_strategy_hints

from src.application.langgraph.reflection.models import (
    ReflectionDecision,
    ReflectionDecisionType,
)
from src.application.langgraph.reflection.strategies.retry_reformulation import (
    KeywordExpansionRetryReformulationStrategy,
    RetryReformulationContext,
    RetryReformulationStrategyRegistry,
)


def _context(**overrides) -> RetryReformulationContext:
    defaults = dict(
        original_user_question="What is the pump seal replacement procedure?",
        answer_intent=None,
        selected_document_id="doc_1",
        reflection_decision=ReflectionDecision(
            decision=ReflectionDecisionType.RETRIEVE_AGAIN,
            confidence=0.9,
            reason="Missing evidence.",
        ),
        top_k=10,
    )
    defaults.update(overrides)
    return RetryReformulationContext(**defaults)


def test_registry_dispatches_each_of_the_five_migrated_intents() -> None:
    registry = RetryReformulationStrategyRegistry()

    for intent in (
        "maintenance",
        "specification",
        "procedure",
        "safety",
        "troubleshooting",
    ):
        strategy = registry.for_intent(intent)
        assert isinstance(strategy, KeywordExpansionRetryReformulationStrategy)


def test_registry_maintenance_strategy_appends_maintenance_expansions() -> None:
    registry = RetryReformulationStrategyRegistry()

    plan = registry.build_retry_plan(
        retrieval_query_intent="maintenance",
        context=_context(
            original_user_question="How often should the pump be serviced?",
            reflection_decision=ReflectionDecision(
                decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                confidence=0.9,
                reason="Missing interval evidence.",
            ),
        ),
    )

    assert "lubrication" in plan.retry_query


def test_registry_falls_back_to_generic_for_an_unregistered_intent() -> None:
    registry = RetryReformulationStrategyRegistry()

    for intent in ("table", "identifier", "overview", "figure", "general", None, ""):
        strategy = registry.for_intent(intent)
        assert isinstance(strategy, KeywordExpansionRetryReformulationStrategy)
        assert strategy is registry.for_intent(None)

    # The generic default has no expansion terms configured -- a fallback
    # query for an unregistered intent must be exactly the question itself,
    # unlike a registered domain intent (proven above to append real terms).
    plan = registry.build_retry_plan(
        retrieval_query_intent="overview",
        context=_context(
            reflection_decision=ReflectionDecision(
                decision=ReflectionDecisionType.RETRIEVE_AGAIN,
                confidence=0.9,
                reason="Missing evidence.",
                retry_query=None,
                missing_information=[],
            )
        ),
    )
    assert plan.retry_query == "What is the pump seal replacement procedure?"


def test_registry_dispatch_is_case_insensitive() -> None:
    registry = RetryReformulationStrategyRegistry()

    assert isinstance(
        registry.for_intent("MAINTENANCE"), KeywordExpansionRetryReformulationStrategy
    )


def test_registry_accepts_custom_strategies_and_default() -> None:
    class _FixedPlanStrategy:
        def build_retry_plan(self, context):
            from src.application.langgraph.reflection.models import RetryPlan

            return RetryPlan(
                retry_query="custom query",
                document_id=context.selected_document_id,
                top_k=context.top_k,
                reason="custom",
            )

    registry = RetryReformulationStrategyRegistry(
        strategies_by_intent={"safety": _FixedPlanStrategy()},
        default_strategy=_FixedPlanStrategy(),
    )

    plan = registry.build_retry_plan(retrieval_query_intent="safety", context=_context())

    assert plan.retry_query == "custom query"
    assert isinstance(registry.for_intent("procedure"), _FixedPlanStrategy)

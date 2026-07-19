from src.application.langgraph.reflection.strategies.clarification import (
    ClarificationContext,
    ClarificationStrategyRegistry,
    FixedOptionsClarificationStrategy,
)


def _context(**overrides) -> ClarificationContext:
    defaults = dict(
        original_user_input="What is the operating pressure?",
        answer_intent=None,
        selected_document_id="doc_1",
        missing_information=[],
    )
    defaults.update(overrides)
    return ClarificationContext(**defaults)


def test_registry_dispatches_maintenance_and_specification_to_fixed_options() -> None:
    registry = ClarificationStrategyRegistry()

    maintenance_options = registry.build_options(
        retrieval_query_intent="maintenance", context=_context()
    )
    specification_options = registry.build_options(
        retrieval_query_intent="specification", context=_context()
    )

    assert maintenance_options == [
        "maintenance tasks",
        "maintenance intervals",
        "maintenance procedures",
    ]
    assert specification_options == [
        "technical specifications",
        "operating limits",
        "dimensions or ratings",
    ]


def test_registry_falls_back_to_missing_information_for_an_unregistered_intent() -> None:
    registry = ClarificationStrategyRegistry()

    options = registry.build_options(
        retrieval_query_intent="troubleshooting",
        context=_context(missing_information=["fault code", "error log"]),
    )

    assert options == ["fault code", "error log"]


def test_registry_falls_back_to_generic_options_with_no_missing_information() -> None:
    registry = ClarificationStrategyRegistry()

    for intent in ("troubleshooting", "safety", "procedure", "overview", None, ""):
        strategy = registry.for_intent(intent)
        assert isinstance(strategy, FixedOptionsClarificationStrategy)

    options = registry.build_options(
        retrieval_query_intent="safety",
        context=_context(missing_information=[]),
    )

    assert options == [
        "the exact section",
        "the exact procedure",
        "the exact specification",
    ]


def test_registry_dispatch_is_case_insensitive() -> None:
    registry = ClarificationStrategyRegistry()

    assert registry.for_intent("MAINTENANCE").build_options(_context()) == [
        "maintenance tasks",
        "maintenance intervals",
        "maintenance procedures",
    ]


def test_registry_accepts_custom_strategies_and_default() -> None:
    class _FixedStrategy:
        def build_options(self, context):
            return ["custom option"]

    registry = ClarificationStrategyRegistry(
        strategies_by_intent={"safety": _FixedStrategy()},
        default_strategy=_FixedStrategy(),
    )

    assert registry.build_options(retrieval_query_intent="safety", context=_context()) == [
        "custom option"
    ]
    assert isinstance(registry.for_intent("procedure"), _FixedStrategy)

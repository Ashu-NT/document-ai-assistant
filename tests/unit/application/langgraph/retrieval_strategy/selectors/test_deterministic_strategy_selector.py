from src.application.langgraph.retrieval_strategy.models import RetrievalContext
from src.application.langgraph.retrieval_strategy.policies import RetrievalStrategyPolicy
from src.application.langgraph.retrieval_strategy.selectors import (
    DeterministicStrategySelector,
)
from src.application.langgraph.retrieval_strategy.services import RetrievalSignalExtractor


def _select(question: str):
    selector = DeterministicStrategySelector()
    extractor = RetrievalSignalExtractor()
    context = RetrievalContext(query_text=question, top_k=5)
    signals = extractor.extract(context)
    return selector.select(
        context=context,
        signals=signals,
        policy=RetrievalStrategyPolicy(),
    )


def test_deterministic_selector_picks_specification_strategy() -> None:
    decision = _select("What is the test pressure and design pressure?")

    assert decision.primary_strategy.value == "TECHNICAL_SPECIFICATION"


def test_deterministic_selector_picks_maintenance_with_table_secondary() -> None:
    decision = _select("What are the maintenance intervals in the schedule table?")

    assert decision.primary_strategy.value == "MAINTENANCE_LOOKUP"
    assert "TABLE_LOOKUP" in [item.value for item in decision.secondary_strategies]


def test_deterministic_selector_picks_table_secondary_for_plain_maintenance_interval_query() -> None:
    decision = _select("What are the maintenance intervals?")

    assert decision.primary_strategy.value == "MAINTENANCE_LOOKUP"
    assert "TABLE_LOOKUP" in [item.value for item in decision.secondary_strategies]
    assert "TECHNICAL_SPECIFICATION" not in [
        item.value for item in decision.secondary_strategies
    ]


def test_deterministic_selector_picks_maintenance_for_required_tasks_question() -> None:
    decision = _select("What maintenance tasks are required for this document?")

    assert decision.primary_strategy.value == "MAINTENANCE_LOOKUP"


def test_deterministic_selector_picks_identifier_lookup() -> None:
    decision = _select("Find part number HAM2423501")

    assert decision.primary_strategy.value == "IDENTIFIER_LOOKUP"


def test_deterministic_selector_picks_troubleshooting_lookup() -> None:
    decision = _select("What is the error cause and remedy for alarm E12?")

    assert decision.primary_strategy.value == "TROUBLESHOOTING_LOOKUP"


def test_deterministic_selector_picks_certification_lookup() -> None:
    decision = _select("Show the certificate approval and compliance information")

    assert decision.primary_strategy.value == "CERTIFICATION_LOOKUP"


def test_deterministic_selector_picks_multi_strategy_for_compare_query() -> None:
    decision = _select("Compare maintenance intervals and technical specifications")

    assert decision.primary_strategy.value == "MULTI_STRATEGY"
    assert "MAINTENANCE_LOOKUP" in [item.value for item in decision.secondary_strategies]
    assert "TECHNICAL_SPECIFICATION" in [
        item.value for item in decision.secondary_strategies
    ]


def test_deterministic_selector_falls_back_to_general_hybrid() -> None:
    decision = _select("Tell me something useful")

    assert decision.primary_strategy.value == "GENERAL_HYBRID"

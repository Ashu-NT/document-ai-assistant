from src.application.langgraph.retrieval_strategy.models import (
    RetrievalContext,
    RetrievalStrategy,
)
from src.application.langgraph.retrieval_strategy.policies import RetrievalStrategyPolicy
from src.application.langgraph.retrieval_strategy.selectors import (
    DeterministicStrategySelector,
)
from src.application.langgraph.retrieval_strategy.services import RetrievalSignalExtractor
from src.application.workflows.retrieval.retrieval_query_analyzer import (
    RetrievalQueryAnalyzer,
)
from src.domain.retrieval import RetrievalQuery


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


def _select_with_full_query_analysis(question: str):
    """Runs the real end-to-end chain: RetrievalQueryAnalyzer (which wires in
    RetrievalQueryChunkTypePreferenceMapper) -> RetrievalSignalExtractor ->
    DeterministicStrategySelector.

    `_select()` above passes `analyzed_query=None`, which means
    `RetrievalSignalExtractor._append_chunk_type_signals` never runs and the
    chunk-type-preference-mapper's contribution to the final decision is
    never exercised. This helper closes that blind spot.
    """
    query = RetrievalQuery(query_id="q_e2e", query_text=question)
    analyzed = RetrievalQueryAnalyzer().analyze(query)
    context = RetrievalContext(query_text=analyzed.query_text, top_k=5, analyzed_query=analyzed)
    signals = RetrievalSignalExtractor().extract(context)
    return DeterministicStrategySelector().select(
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


# --- Full end-to-end chain (P1#5 regression) --------------------------------------
#
# outputs/debug_agent_runtime/maintenance_interval_end_to_end_debug_report.md traced
# a real production bug: "What are the maintenance intervals?" selected
# TECHNICAL_SPECIFICATION as a secondary strategy, via (a) a low-precision
# specification lexical trigger (" a"/" v" matching inside "what are") and
# (b) the MAINTENANCE chunk-type preference list still including
# ChunkType.TECHNICAL_SPECIFICATION. Verified against current code (2026-07-02,
# via git history and direct execution) that both root causes are already
# fixed. These tests exercise the *complete* real chain — including
# RetrievalQueryAnalyzer / RetrievalQueryChunkTypePreferenceMapper, which the
# `_select()` tests above never exercise since they pass `analyzed_query=None` —
# so a regression in either fix would be caught here.

def test_full_chain_plain_maintenance_interval_query_excludes_technical_specification() -> None:
    decision = _select_with_full_query_analysis("What are the maintenance intervals?")

    assert decision.primary_strategy.value == "MAINTENANCE_LOOKUP"
    assert "TABLE_LOOKUP" in [item.value for item in decision.secondary_strategies]
    assert "TECHNICAL_SPECIFICATION" not in [
        item.value for item in decision.secondary_strategies
    ]


def test_full_chain_maintenance_interval_query_variants_exclude_technical_specification() -> None:
    variants = [
        "What are the maintenance intervals?",
        "How often should the filter be replaced?",
        "Is there a maintenance schedule for this equipment?",
        "What maintenance tasks are required for this document?",
    ]

    for question in variants:
        decision = _select_with_full_query_analysis(question)
        secondary_values = [item.value for item in decision.secondary_strategies]

        assert decision.primary_strategy.value == "MAINTENANCE_LOOKUP", question
        assert "TECHNICAL_SPECIFICATION" not in secondary_values, question


def test_full_chain_explicit_specification_query_still_selects_specification() -> None:
    """A genuinely spec-focused query must still surface the specification
    strategy - the maintenance-branch fix must not blind the SPECIFICATION
    branch itself. Under the full chain this query legitimately resolves to
    MULTI_STRATEGY (the SPECIFICATION chunk-type preferences also list
    maintenance/procedure-adjacent chunk types as supporting context), so the
    invariant under test is "specification is present", not "specification is
    the only strategy chosen"."""
    decision = _select_with_full_query_analysis(
        "What is the test pressure and design pressure?"
    )

    all_strategies = {decision.primary_strategy.value} | {
        item.value for item in decision.secondary_strategies
    }
    assert "TECHNICAL_SPECIFICATION" in all_strategies


def test_full_chain_compare_query_still_allows_technical_specification_when_explicitly_asked() -> None:
    decision = _select_with_full_query_analysis(
        "Compare maintenance intervals and technical specifications"
    )

    assert decision.primary_strategy.value == "MULTI_STRATEGY"
    assert "MAINTENANCE_LOOKUP" in [item.value for item in decision.secondary_strategies]
    assert "TECHNICAL_SPECIFICATION" in [
        item.value for item in decision.secondary_strategies
    ]


def test_requested_strategy_is_forced_with_full_confidence() -> None:
    context = RetrievalContext(
        query_text="anything",
        top_k=5,
        requested_strategy=RetrievalStrategy.TABLE_LOOKUP,
    )
    decision = DeterministicStrategySelector().select(
        context=context,
        signals=[],
        policy=RetrievalStrategyPolicy(),
    )

    assert decision.primary_strategy == RetrievalStrategy.TABLE_LOOKUP
    assert decision.confidence == 1.0
    assert decision.secondary_strategies == []


def test_requested_secondary_strategies_are_forced_alongside_the_primary() -> None:
    # Regression guard: a retry recommendation naming more than one
    # plausible strategy (e.g. "could be TABLE_LOOKUP or MAINTENANCE_LOOKUP")
    # previously had no way to carry the second candidate through the
    # forced-strategy branch -- only a single strategy could ever be forced,
    # silently dropping genuine retry-diversification recommendations.
    context = RetrievalContext(
        query_text="anything",
        top_k=5,
        requested_strategy=RetrievalStrategy.TABLE_LOOKUP,
        requested_secondary_strategies=[RetrievalStrategy.MAINTENANCE_LOOKUP],
    )
    decision = DeterministicStrategySelector().select(
        context=context,
        signals=[],
        policy=RetrievalStrategyPolicy(),
    )

    assert decision.primary_strategy == RetrievalStrategy.TABLE_LOOKUP
    assert decision.secondary_strategies == [RetrievalStrategy.MAINTENANCE_LOOKUP]
    assert decision.selected_strategies == [
        RetrievalStrategy.TABLE_LOOKUP,
        RetrievalStrategy.MAINTENANCE_LOOKUP,
    ]

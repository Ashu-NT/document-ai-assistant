from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.retrieval_strategy import (
    RetrievalContext,
    RetrievalStrategy,
    RetrievalStrategyPolicy,
    RetrievalStrategyService,
)
from src.application.langgraph.strategy_advisor import (
    StrategyAdvisorIntent,
    StrategyAdvisorProposal,
)


def test_retrieval_strategy_service_merges_advisor_strategies_without_removing_deterministic_baseline() -> None:
    service = RetrievalStrategyService(
        policy=RetrievalStrategyPolicy(
            enabled=True,
            llm_strategy_enabled=True,
            max_strategies_per_query=4,
        )
    )

    result = service.select_and_plan(
        RetrievalContext(
            query_text="compare troubleshooting procedures and maintenance tasks",
            route="answer_question",
            top_k=5,
            use_llm_selector=True,
            strategy_advisor_proposal=StrategyAdvisorProposal(
                intent=StrategyAdvisorIntent.COMPARISON,
                route="deep_research",
                confidence=0.92,
                concepts=["troubleshooting", "maintenance", "procedures"],
                recommended_strategies=[
                    RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
                    RetrievalStrategy.MAINTENANCE_LOOKUP,
                    RetrievalStrategy.PROCEDURE_LOOKUP,
                ],
                comparison=True,
                requires_table=False,
                reason="The request compares multiple concepts.",
            ),
        ),
        tool_registry=ToolRegistry(retrieve_chunks_tool=object()),
    )

    assert result.decision.primary_strategy == RetrievalStrategy.MULTI_STRATEGY
    assert result.decision.selected_strategies[0] == RetrievalStrategy.MAINTENANCE_LOOKUP
    assert set(result.decision.selected_strategies) == {
        RetrievalStrategy.MAINTENANCE_LOOKUP,
        RetrievalStrategy.PROCEDURE_LOOKUP,
        RetrievalStrategy.TROUBLESHOOTING_LOOKUP,
    }
    assert result.trace.advisor_status == "accepted"
    assert any(
        event["name"] == "StrategyMerged"
        for event in result.trace.advisor_events
    )

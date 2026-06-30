from src.application.langgraph.factories import ToolRegistry
from src.application.langgraph.retrieval_strategy.models import (
    RetrievalStrategy,
    RetrievalStrategyDecision,
)
from src.application.langgraph.retrieval_strategy.planners import RetrievalPlanBuilder
from src.application.langgraph.retrieval_strategy.policies import RetrievalStrategyPolicy
from src.application.langgraph.retrieval_strategy.validation import (
    RetrievalPlanValidator,
)


def test_retrieval_plan_builder_uses_retrieve_tables_when_available() -> None:
    builder = RetrievalPlanBuilder()
    decision = RetrievalStrategyDecision(
        primary_strategy=RetrievalStrategy.TABLE_LOOKUP,
        query="show the table",
        top_k=5,
    )

    plan = builder.build(
        decision,
        tool_registry=ToolRegistry(
            retrieve_chunks_tool=object(),
            retrieve_tables_tool=object(),
        ),
        policy=RetrievalStrategyPolicy(),
    )

    assert plan.steps[0].tool_name == "retrieve_tables"


def test_retrieval_plan_validator_falls_back_to_retrieve_chunks_when_table_tool_missing() -> None:
    builder = RetrievalPlanBuilder()
    validator = RetrievalPlanValidator()
    decision = RetrievalStrategyDecision(
        primary_strategy=RetrievalStrategy.TABLE_LOOKUP,
        query="show the table",
        top_k=5,
    )

    plan = builder.build(
        decision,
        tool_registry=ToolRegistry(retrieve_chunks_tool=object()),
        policy=RetrievalStrategyPolicy(),
    )
    validated = validator.validate(
        plan,
        tool_registry=ToolRegistry(retrieve_chunks_tool=object()),
        policy=RetrievalStrategyPolicy(),
    )

    assert validated.steps[0].tool_name == "retrieve_chunks"
